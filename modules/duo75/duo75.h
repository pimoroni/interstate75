// Include MicroPython API.
#include "py/runtime.h"
#include "py/objstr.h"

/***** Extern of Class Definition *****/
extern const mp_obj_type_t Duo75_type;

/***** Extern of Class Methods *****/
extern void Duo75_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind);
extern mp_obj_t Duo75_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args);
extern mp_obj_t Duo75___del__(mp_obj_t self_in);
extern mp_obj_t Duo75_start(mp_obj_t self_in);
extern mp_obj_t Duo75_stop(mp_obj_t self_in);
extern mp_obj_t Duo75_update(mp_obj_t self_in, mp_obj_t graphics_in);
extern mp_obj_t Duo75_is_busy(mp_obj_t self_in);
extern mp_obj_t Duo75_set_blocking(mp_obj_t self_in, mp_obj_t blocking_in);