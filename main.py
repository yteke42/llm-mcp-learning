import asyncio

from agent import run_agent


async def main():

    print("Technical Publishing Agent")
    print("--------------------------")

    user_input = input("\nYou: ")

    answer = await run_agent(
        user_input
    )

    print("\nAgent:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())