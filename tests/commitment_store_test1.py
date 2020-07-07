import time
from loguru import logger

from pyargcbr.agents import CommitmentStore
from pyargcbr.agents import DebugAgent

if __name__ == "__main__":
    cs = CommitmentStore("commitment_store@localhost", "secret")
    agent = DebugAgent("debug_agent@localhost", "secret")
    logger.info("Running Agents")
    cs.start()
    agent.start()
    logger.info("Wait until user interrupts with ctrl+C")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
    cs.stop()
    logger.info("Stopping Agent")
