import asyncio
import logging

from tasks import certificate_taxi, city_partners 


main_logger = logging.getLogger(__name__)

async def main():
    try:
        await certificate_taxi()
        #await city_partners()
    except Exception as err:
        main_logger.info(f"[-] Err starting app: {str(err)}")

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())

finally:
    pending = asyncio.all_tasks(loop)

    if pending:
        loop.run_until_complete(asyncio.gather(*pending))

    main_logger.info('[+] Closing the event loop...')
    loop.close()
