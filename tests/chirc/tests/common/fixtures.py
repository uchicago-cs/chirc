channels1 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user4", "user5", "user6"),
              "#test3": ("@user7", "user8", "user9")
            }

channels2 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user4", "user5", "user6"),
              "#test3": ("@user7", "user8", "user9"),
                  None: ("user10" , "user11")
            }
                
channels3 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user2",),
              "#test3": ("@user3", "@user4", "user5", "user6"),
              "#test4": ("@user7", "+user8", "+user9", "user1", "user2"),
              "#test5": ("@user1", "@user5"),
                  None: ("user10" , "user11")
            }                
                
channels4 = { None: ("user1", "user2", "user3", "user4", "user5") }