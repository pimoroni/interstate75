// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME                   "Interstate 75 Duo"

#define MICROPY_HW_FLASH_STORAGE_BYTES          (PICO_FLASH_SIZE_BYTES - (2 * 1024 * 1024))

// Set up networking.
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT     "I75Duo"

// Enable WiFi & PPP
#define MICROPY_PY_NETWORK                      (1)

// CYW43 driver configuration.
#define CYW43_USE_SPI                           (1)
#define CYW43_LWIP                              (1)
#define CYW43_GPIO                              (1)
#define CYW43_SPI_PIO                           (1)

#ifndef CYW43_WL_GPIO_COUNT
#define CYW43_WL_GPIO_COUNT 3
#endif

#define MICROPY_HW_PIN_EXT_COUNT    CYW43_WL_GPIO_COUNT

int mp_hal_is_pin_reserved(int n);
#define MICROPY_HW_PIN_RESERVED(i) mp_hal_is_pin_reserved(i)

// Enable PSRAM
#define MICROPY_HW_ENABLE_PSRAM                 (1)

// Alias the chip select pin specified by presto.h
#define MICROPY_HW_PSRAM_CS_PIN                 PIMORONI_I75DUO_PSRAM_CS_PIN

#define MICROPY_PY_THREAD                       (0)
