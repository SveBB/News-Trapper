from db_controller import DBController
dbc = DBController()

#dbc.add_user("123")

#dbc.add_source("123", "lenta, ria")

#dbc.add_update_n("123", 3)



ls = dbc.from_source()
for i in ls:
    print(i)
