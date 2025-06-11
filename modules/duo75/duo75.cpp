#include <cstdio>
#include "drivers/duo75/duo75.hpp"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "pico/multicore.h"

#include "micropython/modules/util.hpp"


using namespace pimoroni;

extern "C" {
#include "duo75.h"
#include "py/builtin.h"
#include "py/mpthread.h"
#include "micropython/modules/pimoroni_i2c/pimoroni_i2c.h"

void __printf_debug_flush() {
    for(auto i = 0u; i < 10; i++) {
        sleep_ms(2);
        mp_event_handle_nowait();
    }
}

int mp_vprintf(const mp_print_t *print, const char *fmt, va_list args);

#if DEBUG
void duo75_debug(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = mp_vprintf(&mp_plat_print, fmt, ap);
    va_end(ap);
    __printf_debug_flush();
    (void)ret;
}
#else
#define duo75_debug(fmt, ...)
#endif

typedef struct _ModPicoGraphics_obj_t {
    mp_obj_base_t base;
    PicoGraphics *graphics;
    DisplayDriver *display;
    void *spritedata;
    void *buffer;
    void *fontdata;
    _PimoroniI2C_obj_t *i2c;
    bool blocking = true;
    uint8_t layers;
} ModPicoGraphics_obj_t;

typedef struct _mp_obj_float_t {
    mp_obj_base_t base;
    mp_float_t value;
} mp_obj_float_t;

const mp_obj_float_t const_float_1 = {{&mp_type_float}, 1.0f};
const uint DUO75_WIDTH = 128;
const uint DUO75_HEIGHT = 128;

/********** WS2812 **********/

/***** Variables Struct *****/
typedef struct _Duo75_obj_t {
    mp_obj_base_t base;
    Duo75* duo75;
    void *buf;
    volatile bool exit_core1;
    // Automatic ambient backlight control
    volatile bool auto_ambient_leds;
    volatile bool blocking;
    volatile bool flip;
    PicoGraphics *graphics;
} _Duo75_obj_t;

_Duo75_obj_t *duo75_obj;


void __isr dma_complete() {
    if(duo75_obj) duo75_obj->duo75->dma_complete();
}

#define stack_size 1024u
static uint32_t core1_stack[stack_size] = {0};

void duo75_core1_entry() {
    // The multicore lockout uses the FIFO, so we use just use sev and volatile flags to signal this core
    multicore_lockout_victim_init();

    duo75_obj->duo75->start(dma_complete);

    multicore_fifo_push_blocking(0); // TODO: handle issues here?

    // Duo75 is now running the display using interrupts on this core.
    // We can also drive the backlight if requested.
    while (true) {
        if (duo75_obj->exit_core1) {
            break;
        }
        if (duo75_obj->flip) {
            duo75_obj->duo75->update(duo75_obj->graphics);
            duo75_obj->flip = false;
        }
    }

    duo75_obj->duo75->stop(dma_complete);

    multicore_fifo_push_blocking(0);
}

void duo75_core1_start() {
    duo75_debug("launch core1\n");
    multicore_reset_core1();
    duo75_obj->exit_core1 = false;
    duo75_obj->flip = false;

    // Micropython uses all of both scratch memory (and more!) for core0 stack, 
    // so we must supply our own small stack for core1 here.
    multicore_launch_core1_with_stack(duo75_core1_entry, core1_stack, stack_size);
    duo75_debug("launched core1\n");

    int res = multicore_fifo_pop_blocking();
    duo75_debug("core1 returned\n");

    if(res != 0) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Hub75 Duo: failed to start Core1."));
    }
}

void duo75_core1_stop() {
    duo75_debug("signal core1\n");
    duo75_obj->flip = false;
    duo75_obj->exit_core1 = true;
    __sev();

    int fifo_code;
    do {
        fifo_code = multicore_fifo_pop_blocking();
        if (fifo_code == 1) {
            // TODO: LED cleanup here
        }
    } while (fifo_code != 0);

    duo75_debug("core1 returned\n");
}

/***** Print *****/
void Duo75_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)self_in;
    (void)kind;
    mp_print_str(print, "Duo75(128x128)");
}

/***** Destructor ******/
mp_obj_t Duo75___del__(mp_obj_t self_in) {
    (void)self_in;
    duo75_core1_stop();
    m_del_class(Duo75, duo75_obj->duo75);
    duo75_obj->duo75 = nullptr;
    duo75_obj = nullptr;
    return mp_const_none;
}

/***** Constructor *****/
mp_obj_t Duo75_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum { 
        ARG_buffer,
    };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_buffer, MP_ARG_OBJ, {.u_obj = nullptr} }
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    Pixel *buffer = nullptr;

    if (args[ARG_buffer].u_obj) {
        mp_buffer_info_t bufinfo;
        mp_get_buffer_raise(args[ARG_buffer].u_obj, &bufinfo, MP_BUFFER_RW);
        buffer = (Pixel *)bufinfo.buf;
        if(bufinfo.len < (size_t)(DUO75_WIDTH * DUO75_HEIGHT * sizeof(Pixel))) {
            mp_raise_ValueError(MP_ERROR_TEXT("Supplied buffer is too small!"));
        }
    } else {
        buffer = m_new(Pixel, DUO75_WIDTH * DUO75_HEIGHT);
    }

    duo75_obj = mp_obj_malloc_with_finaliser(_Duo75_obj_t, &Duo75_type);
    duo75_obj->buf = buffer;
    duo75_obj->duo75 = m_new_class(Duo75, buffer);
    duo75_obj->blocking = false;
    duo75_obj->flip = false;

    return MP_OBJ_FROM_PTR(duo75_obj);
}

mp_obj_t Duo75_set_blocking(mp_obj_t self_in, mp_obj_t blocking_in) {
    (void)self_in;
    duo75_obj->blocking = mp_obj_is_true(blocking_in);
    return mp_const_none;
}

mp_obj_t Duo75_is_busy(mp_obj_t self_in) {
    (void)self_in;
    return mp_obj_new_bool(duo75_obj->flip);
}

mp_obj_t Duo75_update(mp_obj_t self_in, mp_obj_t graphics_in) {
    (void)self_in;
    ModPicoGraphics_obj_t *picographics = MP_OBJ_TO_PTR2(graphics_in, ModPicoGraphics_obj_t);

   if(!duo75_obj->blocking) {

        while(duo75_obj->flip) {};

        duo75_obj->graphics = picographics->graphics;
        duo75_obj->flip = true;
        __sev();

    } else {

        duo75_obj->duo75->update(picographics->graphics);

    }

    return mp_const_none;
}

mp_obj_t Duo75_start(mp_obj_t self_in) {
    (void)self_in;
    duo75_core1_start();
    return mp_const_none;
}

mp_obj_t Duo75_stop(mp_obj_t self_in) {
    (void)self_in;
    duo75_core1_stop();
    return mp_const_none;
}

}