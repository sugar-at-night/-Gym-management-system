# Lincoln Fitness Management System

The Fitness Club Management System is a comprehensive system designed to efficiently manage the membership, trainers, and classes of a fitness club. The system is targeted towards Admin/
Managers, Members, and Trainers, each with their respective functionalities. 

## Access
**Host**: http://yan2023.pythonanywhere.com/

There are three roles defined in the system
- Member
- Admin/Manager
- Trainer

------------


Each role has its own view and functionality once they log in. 
**Member **
- Can edit their profile
- Can Enrol Group Class
- Can Enrol Personal training session
- Cancel Group enrolled
- Can cancel the personal class if the payment status is still pending.
- Can update their monthly subscription

**Trainer**
- Can create a training session
- Can see their own session
- Can update their profile

**Admin/Manager**
- Can add a new member
- Can add/update/delete training class
- Can add/update/delete personal training
- Can configure notification.
- Can see notification logs
- Can see payment logs
- Can see reports

------------

## Main Routes
`/`
`/login`
`/logout`
`/member`
`/training`
`/class`
`/notificationconfig`
`/report`
`/attendance`

------------

## License

[@Lincoln Fitness]()
