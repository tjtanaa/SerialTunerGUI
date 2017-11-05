#include "ch.h"
#include "hal.h"

#include "params.h"
#include "flash.h"
#include  <string.h>

#define PARAM_FLASH_SECTOR           11U
#define PARAM_FLASH_ADDR      0x080E0000

#define PARAM_FLASH_HALF_BLOCK       64U
#define PARAM_FLASH_BLOCK           128U

static p_param_t    params[PARAMS_NUM_MAX];
static uint8_t      subparams[PARAMS_NUM_MAX][8];
static uint8_t      params_total = 0;
static uint8_t      subparams_total = 0;

#define RXBUF_SIZE 7
static uint8_t rxbuf[RXBUF_SIZE];
static thread_reference_t uart_receive_thread_handler = NULL;

/* Private functions*/
static void param_save_flash(void);

static THD_WORKING_AREA(params_tx_wa, 128);
static THD_FUNCTION(params_tx,p)
{
  chRegSetThreadName("param transmitter");
  (void)p;
  chThdSleepMilliseconds(10);

  uartStopSend(UART_PARAMS);
  uartStartSend(UART_PARAMS, 1, &params_total);
  chThdSleepMilliseconds(50);

  uartStopSend(UART_PARAMS);
  uartStartSend(UART_PARAMS, 1, &subparams_total);
  chThdSleepMilliseconds(50);

  uartStopSend(UART_PARAMS);
  uartStartSend(UART_PARAMS, 8*params_total, subparams[0]);
  chThdSleepMilliseconds(50);

  uint8_t i;
  for(i = 0; i<params_total; i++)
  {
    uartStopSend(UART_PARAMS);
    uartStartSend(UART_PARAMS, 4*subparams[i][0], (uint8_t*)(params[i]));
    chThdSleepMilliseconds(50);
  }

  chThdExit(MSG_OK);
}

/*
 * This callback is invoked when a receive buffer has been completely written.
 */
static void rxend(UARTDriver *uartp)
{
  if(uartp == UART_PARAMS)
  {
    switch(rxbuf[0])
    {
      case 'p':
        if(rxbuf[1] < params_total && rxbuf[2] < subparams[rxbuf[1]][0])
        {
          chSysLockFromISR();
          params[rxbuf[1]][rxbuf[2]] = *((param_t*)(rxbuf+3));
          chSysUnlockFromISR();
        }
        break;
      case 's':
        if(rxbuf[1] < params_total && rxbuf[2] < subparams[rxbuf[1]][0])
          subparams[rxbuf[1]][rxbuf[2] + 1] = rxbuf[3];
        break;
      case 'u':
        param_save_flash();
        break;
      case 'g':
        chSysLockFromISR();
        thread_t* uart_transmit_thread = chThdCreateI(params_tx_wa,sizeof(params_tx_wa),
          NORMALPRIO - 7,params_tx,NULL);
        chThdStartI(uart_transmit_thread);
        chSysUnlockFromISR();
        break;
    }

    chSysLockFromISR();
    chThdResumeI(&uart_receive_thread_handler,MSG_OK);
    chSysUnlockFromISR();
  }
}

/*
 * UART driver configuration structure.
 */
static UARTConfig uart_cfg = {
  NULL,NULL,rxend,NULL,NULL,
  115200,
  0,
  0,
  0
};

static THD_WORKING_AREA(params_rx_wa, 128);
static THD_FUNCTION(params_rx,p)
{
  chRegSetThreadName("param receiver");
  (void)p;

  while(!chThdShouldTerminateX())
  {
    uartStartReceive(UART_PARAMS, RXBUF_SIZE, rxbuf);

    chSysLock();
    chThdSuspendS(&uart_receive_thread_handler);
    chSysUnlock();
  }
}

static void param_save_flash(void)
{
  flashSectorErase(PARAM_FLASH_SECTOR);
  uint8_t i;

  flashaddr_t address = PARAM_FLASH_ADDR + 16;
  for(i = 0; i<params_total; i++)
  {
    flashWrite(address,subparams[i],8);
    flashWrite(address + PARAM_FLASH_HALF_BLOCK,
      (char*)(params[i]), subparams[i][0]*4);
    address += PARAM_FLASH_BLOCK;
  }
}



static uint8_t param_load_flash(const uint8_t param_pos, const uint8_t param_num)
{
  uint8_t result = 0;

  flashaddr_t address = PARAM_FLASH_ADDR + 16 +
                        param_pos*PARAM_FLASH_BLOCK;
  flashRead(address,subparams[param_pos],8);

  uint8_t i;
  if(subparams[param_pos][0] == 0xFF)
  {
    for(i = 0; i < 8; i++)
      subparams[param_pos][i] = 0;
    subparams[param_pos][0] = param_num;
  }

  flashRead(address + PARAM_FLASH_HALF_BLOCK,
            (char*)(params[param_pos]), subparams[param_pos][0]*4);

  for (i = 0; i < param_num; i++)
    //Check the validity of the read-out value
    if(params[param_pos][i] != params[param_pos][i] ||
       params[param_pos][i] > 1.701411e38 ||
       params[param_pos][i] < -1.701411e38)
    {
      params[param_pos][i] = 0.0f;
      result = 1;
    }
  return result;
}

uint8_t params_set(param_t* const     p_param,
                  const uint8_t      param_pos,
                  const uint8_t      param_num)
{
  //Maximum num of parameters and subparameters supported
  if(param_pos != params_total || param_pos > PARAMS_NUM_MAX - 1 || param_num > 7)
    return 1;

  uint8_t result = 0;
  params[param_pos] = p_param;
  subparams[param_pos][0] = param_num;

  if(param_load_flash(param_pos, param_num))
  {
    subparams[param_pos][0] = param_num;
    result = 2;
  }

  params_total++;
  subparams_total += param_num;

  return result;
}

void params_init(void)
{
  uartStart(UART_PARAMS, &uart_cfg);
  chThdCreateStatic(params_rx_wa,sizeof(params_rx_wa),
    NORMALPRIO + 7,params_rx,NULL);
}
