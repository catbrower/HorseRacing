# HorseRacing

Repo for building an ML Model and dataset to bet on horses

Current work: assemble dataset by scraping equibase and using weather api
Weather website has an api so it's the most simple taks
Scraping equibase has three parts
* Scrape which races occured by day
* Scrape a pdf which holds the race details
* Use Tesseract OCR to extract pdf data

Freddy,
You can do one or all three of the follwing. Dont worry about OCR or the ML stuff
Easiest thing to do is just scrape the weather site
For equibase, scraping races by day should be easy. Getting the pdfs will be more difficult
For all data extraction the start date will always be Jan 1 1991. The reason for this is that it is the furthest back equibase goes
The date_to will always be whatever today is. Write a function that just gets todays date and returns it so I don't have to manually update it whenever I actually run this thing
LMK if you have an Qs or if you don't really want to do it which is totally fine don't sweat it
Thanks!

# Weather site details:
Scraper exists in weather_data_ripper.py
There is an example URL at the top
You can only request weather data for one month at a time
The API is sensitive with regards to how you specify dates. You can't just ask for July you have to specify July you can't hard code it to always ask Month 1 - Month 31 as it will throw an error for months with < 31 days. To get around this you can use a datetime object, add to it one timedelta month, then subtract one day. I did a little experiment in the ripper to test this so just use that unless you find a better way.
Once you get the response, just extract the useful data from the body and dump it as-is into mongodb, I'll figure a way later to put it together into a nice dataset later

# Equibase:
Equibase sells horse racing data, consequently they have some anti-scraping tech. However, this can be circumvented.
The file equibase_ripper.py has the basic setup to circumvent their website security so you don't need to figure that out
The only logic you need to concentrate on is how to generate the necessary URLs, extract the relevant data from the page, save to mongo

Part 1: Determine which races happened on which days
Problem: Tracks i.e Saratoga don't race every day. So if I want to get all of saratoga's data I have to query which days they have races which I don't know in advance. Solution: Just download everything and figure it out afterwards.
It is reasonable to assume that there is atleast one race happening somewhere in the world for every day
This data needs to be collected as it is necessary for part two (the more complex part) and is needed to check for data integrity later on (did we actually scrape everything we wanted?)
In the equibase file is an example url for race by day, you can see in the url params how to specify the date
I think a triple nested loop for day, month, year will suffice
To make this code reusable specify at the top a date_from and date_to variable so if something is missed it's easy to specify the missing date and rerun it

Part 2: Pull the PDFs
Like I said this one is likely to be more difficult.
You will have to read from mongo all the race data from part one and use that to build a URL to grab a pdf, see the example URL in the equibase ripper
This function would need to be written in a specific way to make it easily usable with the OCR. Specifically, it needs to be a loop that iterates over all possible PDF files and yields each one. I want to do it this way specifically so I can write the code like this:
for pdf in get_all_pdfs():
    do_ocr(pdf)

Equibase considerations:
Given that they do have some degree of anti-bot technology it is likely that you might encounter some issues pulling data
I haven't testing it thouroughly but I suspect they probably have some ability to see how quickly pages are being requested and consequntly throttle you.
It might also be that they have a maximum requests / time sort of thing setup. If they do, you'll have to code in a time.sleep() to account for this