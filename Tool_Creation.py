from langchain_classic.tools import Tool

import Help_Assist
import NPC
import VPM

def create_tools_new(agents, session_id):

    def npc_tool(time_period:str):
        file_path = agents[session_id]["latest_file"]
        try:
            file_name = file_path["filename"]
            print(file_name)
            
            return NPC.npc(time_period, file_name)
        except Exception as e:
            return f"Please upload the file with future prices to perform NPC analysis." 
    
    def help_assist_tool(query: str):
        return Help_Assist.Help_Assist(query)

    def vpm_tool(time_period: str):
        return VPM.vpm(time_period)

    print("Tools created successfully")
    return [
        Tool(
            name="NPC_Tool",
            func=npc_tool,
            return_direct=True,
            description="""
            Use this tool to perform simulations and data analysis based on the sales data and future prices.
            Whenever user asks for performing simulation or impact analysis for future price changes, use this tool to analyze the sales data and future prices and provide insights on the impact of future price changes on revenue.
            ONLY USE THIS TOOL when the user wants to simulate or compare FUTURE price changes impact on revenue.
            If time period is not provided, assume it to be 12 months.

            Examples:
            - Simulate the impact of future price changes on revenue
            - What will be the revenue if we change the price of an item to X
            - Compare the revenue for current prices vs future prices based on the attached file
            - Compare revenue with new pricing CSV

            DO NOT use for:
            - past price changes analysis
            - help questions

            The return value of NPC tool is the final answer. Do not continue reasoning after getting the output from NPC tool.
            """
        ),
        Tool(
            name="Help_Assist_Tool",
            func=help_assist_tool,
            return_direct=True,
            description="""
            Use this tool to provide assistance and answer questions based on the user guide.
        Whenever a user asks a question about how to do pricing or regarding any steps involved in Pricing, use this tool to provide guidance based on user guide.
        Always use this tool for questions related to pricing steps, pricing process, or any guidance related to pricing. 
        Only use it when the question is about how to do pricing or any steps involved in pricing.     

        Examples:
        - How to set prices for an item or a customer
        - What are the steps involved in pricing
        - Can you guide me through the pricing process

        DO NOT USE THIS TOOL for:
        - simulations
        - data analysis
        - historical analysis
        - KPI's such as (Revenue, Profit, Margin, Discount, Volumne, etc.) related questions

        The output of the Help_Assist tool should be a concise and clear answer to the user's question based on the user guide. Always provide step by step guidance if the question is related to how to do pricing.
        """
        ),
        Tool(
            name="VPM_Tool",
            func=vpm_tool,
            return_direct=True,
            description="""
            Use this tool to perform histoirical anlaysis on sales data.
            Whenever user asks for imapct of historical price changes on revenue, use this tool to provide them with Insights on how historical price changes have impacted revenue based on the sales data.
            ONLY USE THIS TOOL when the user wants to analyze the impact of historical price changes on revenue.
            If time period is not provided, assume it to be 12 months.

            Examples:
            - Analyze the impact of historical price changes on revenue
            - What was the revenue impact of last changed price in past 12 months
            - Give me the Volume Effect, Price Effect, and Mix Effect of historical price changes considering last 3 months

            DO NOT use for:
            - future price changes analysis
            - help questions

            The output of the VPM tool should be a list with three values: [price_effect, volume_effect, mix_effect], where price_effect is the impact on revenue due to price changes, volume_effect is the impact on revenue due to volume changes, and mix_effect is the impact on revenue due to the interaction of price and volume changes.
            """)
    ]
