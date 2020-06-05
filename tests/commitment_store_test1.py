import time

from agents.commitment_store_agent import CommitmentStore
from agents.debug_agent import DebugAgent

if __name__ == "__main__":
    cs = CommitmentStore("commitment_store@localhost", "secret")
    agent = DebugAgent("debug_agent@localhost", "secret")
    print("Running Agents")
    cs.start()
    agent.start()
    print("Wait until user interrupts with ctrl+C")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
    cs.stop()
    print("Stopping Agent")
