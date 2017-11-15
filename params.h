#ifndef _PARAMS_H_
#define _PARAMS_H_

#define UART_PARAMS &UARTD3
#define PARAMS_NUM_MAX        32U

typedef float param_t, *p_param_t;

uint8_t params_set(param_t* const     p_param,
                  const uint8_t      param_pos,
                  const uint8_t      param_num,
                  const char* const  Param_name,
                  const char* const  subParam_name,
                  param_public_flag_t param_private);
void params_init(void);

#endif
