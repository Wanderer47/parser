import asyncio
import logging

from parsing_services import certificate_taxi, add_in_the_file, start_parsing


logger = logging.getLogger(__name__)


async def main():
    try:
        await certificate_taxi(add_in_the_file)
        await start_parsing()
    except Exception as err:
        logger.info(f"[-] Err starting app: {str(err)}")

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())

finally:
    pending = asyncio.all_tasks(loop)

    if pending:
        loop.run_until_complete(asyncio.gather(*pending))

    logger.info('[+] Closing the event loop...')
    loop.close()
