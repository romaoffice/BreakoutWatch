import datetime
date_str = '2022_10_01'
date_object1 = datetime.datetime.strptime(date_str, "%Y_%m_%d").date()
date_str = '2022_10_03'
date_object2 = datetime.datetime.strptime(date_str, "%Y_%m_%d").date()
dayspan = date_object2-date_object1
print (dayspan.days)