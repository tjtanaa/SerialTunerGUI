#ifndef _PARAMS_H_
#define _PARAMS_H_

#define UART_PARAMS &UARTD3
#define PARAMS_NUM_MAX        20U

typedef float param_t, *p_param_t;

uint8_t params_set(param_t* const     p_param,
                const uint8_t      param_pos,
                const uint8_t      param_num);
void params_init(void);

#endif
