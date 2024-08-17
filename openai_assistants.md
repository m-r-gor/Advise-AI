**Below are instructions/settings for all the OpenAI Assistants used.**
---

**write_reply**  
Instructions:  
```  
```  
---  

**determine_elements**  
Instructions:  
```  
```  
---  

**adjust_to_context**  
Instructions:  
```  
```  
---  

**adjust_to_advisor_style**  
Instructions:  
```  
```  
---  

**RAGneed_docselect**  
Instructions:  
```  
```  
---  

**verify_content_RAG**  
Instructions:  
```  
```  
---  

**final_context_check**  
Instructions:  
```  
```  
---  

**DOC_tax**  
Instructions:  
```  
```  
---  

**DOC_mackenzie**  
Instructions:  
```  
```  
---  

**rewrite_query**  
Instructions:  
```  
```  
---  

**searchforfunds**  
Instructions:  
```  
```  
---  

**determine_if_portfolio_related**  
Instructions:  
```  
```  
---  

**intercept_if_portfolio_related**  
Instructions:  
```  
```  
---  

**recognize_client**  
Instructions:  
```  
```  
---  

**provide_experts**  
Instructions:  
```  
```  
---  

**provide_attachments**  
Instructions:  
```  
```  
---  

**provide_relevant_products**  
Instructions:  
```
You will be provided with the profile of a client of a financial advisor. Below is a list of criteria for recommending financial products. Output a json file with products from the options below that are relevant based on the client info provided, and a statement for each product that mentions the criteria they met and explains what action they should take. Vary the way you begin the statements so that sometimes they start with "Given" and sometimes they don't. Write "Client" instead of using the client's name.

Criteria:

- If the client has a portfolio value of over $1M, moderate or agressive risk profile, and long investment horizon: private asset funds

- LIFE INSURANCE (
If the client has a portfolio of greater than $1M and owns a business: par-whole life insurance
Else if the client has a family, and has a portfolio of over $1M: whole life insurance
Else if the client has a family: term life insurance
) (note: if the client meets criteria for more than one time of life insurance, only reccomend one)

- If the client's household relies on a single income: disability and critical illness insurance

- If client has a mortgage that doesn't renew soon, or plans on buying a property/home/condo within the next 3 months: creditor insurance

- If the client's mortgage is up for renewal within the next 6 months: mortgage

Output should be in json format, with product names in lowercase, with no additional commentry. 

Example output: {"creditor insurance": "Given client has a mortage, they should consider creditor insurance in order to ensure family is secure in case of unexpected events like death, disability, or critical illness",  "product 2":  "Concise rationale for recommending product 2"}
```
Temperature: *0.9*
Response: *json_object*
---  

**determine_meeting_time**  
Instructions:  
```
You will be provided with an email a financial advisor received from a client in the Toronto timezone (-04:00), as well as the response the advisor wrote. Determine a proposed start time, end time, title, description, and location (if any) and output the info in json format, like this:

{'title': 'Meeting with Tim', 'start_datetime': '2024-07-30T10:00:00-04:00', 'end_datetime': ''2024-07-30T11:00:00-04:00', 'description': 'Lunch and discussion regarding life insurance options', 'location': 'Ferriera Cafe'}

If the meeting is taking place at a restaurant, include the provided driving time in the description. If no location is specified, make it '751 Rue du Square-Victoria'. There should be no spaces in the start time and end time.
```
Response: *json_object*
---  

**recap_enquiry**  
Instructions:  
```
You will be provided with an email a financial advisor recieved from a client. Write a summary of the client enquiry. The summary is for the advisor to read, so use "you" instead of "the advisor" or "Sam". Write "Client" instead of using the client's name. Output strictly the summary with no title/heading.
```  
---  

**schedule_meeting_instead**  
Instructions:  
```  
```  
---  

**remove_detail**  
Instructions:  
```  
```  
---  

**add_detail**  
Instructions:  
```  
```  
---  

**more_casual**  
Instructions:  
```  
```  
---  

**make_friendly**  
Instructions:  
```  
```  
---  

**make_professional**  
Instructions:  
```  
```  
---  

**change_custom**  
Instructions:  
```  
```  
---  

**translate**  
Instructions:  
```  
```  
---  

**determine_salesopps**  
Instructions:  
```  
```  
---





