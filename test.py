import streamlit as st
import mysql.connector as connector

con=connector.connect(host='localhost',
                  port='3306',
                  user='root',
                  password='root',
                  database='test')

#print(con)
#query = 'create table if not exists customer(accountnumber number(10) primary key check (accountnumber between 1000000000 and 9999999999), name varchar(25),password varchar(25))'
cur=con.cursor()



def create_custtable():
    cur.execute('create table if not exists customer(accountnumber int primary key check (accountnumber between 1000000000 and 9999999999) , name varchar(25),password varchar(25))')
    con.commit()

#create_custtable()
def create_accttable():
    cur.execute('create table if not exists account(accountnumber int primary key,FOREIGN KEY(accountnumber) REFERENCES customer(accountnumber), balance float DEFAULT 0)')
    con.commit()




def add_cust(accountnumber,name,password):
    cur.execute('INSERT INTO customer(accountnumber,name,password) VALUES(%(accountnumber)s,%(name)s,%(password)s)',
                {
        'accountnumber':accountnumber,
        'name':name,
        'password':password,
                })
    cur.execute('INSERT INTO account(accountnumber) VALUES(%(accountnumber)s)',
                {
        'accountnumber':accountnumber,
                })
    con.commit()

def deposit(balance,accountnumber):
    cur.execute('UPDATE account set balance=balance + %(balance)s where accountnumber=%(accountnumber)s',
                {
        'balance':balance,
        'accountnumber':accountnumber,
                })
    con.commit()

def showbal(accountnumber):
    cur.execute('SELECT balance from account where accountnumber=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    
    
    for (i) in cur:
        st.write(i[0])
    con.commit()
    



def login(accountnumber,Password):
    cur.execute('SELECT accountnumber,password FROM customer WHERE accountnumber=%s AND password =%s',(accountnumber,Password))
    data=cur.fetchall()
    return data

#print("Created")



def main():
    st.title("Onlline Banking App")

    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home")
    
    elif choice == "Login":
        st.subheader("Login section")

        accountnumber = st.sidebar.text_input("Acc.no")
        Password = st.sidebar.text_input("Password",type = 'password')
        if st.sidebar.checkbox("Login"):
            create_custtable()
            create_accttable()
            result = login(accountnumber,Password)
            if result:

                st.success("Logged In as {}".format(accountnumber))

                task = st.selectbox("Action",['Deposit','Withdraw','Check Balance','Transfer'])
                if task == "Deposit":
                    st.subheader("Deposit money")
                    money = st.number_input("Money",min_value =10.00,max_value=1000000.00)
                    if st.button("deposit"):
                        deposit(money,accountnumber)
                        st.success("money added")

                elif task == "Withdraw":
                    st.subheader("withdraw")

                elif task == "Check Balance":
                    st.subheader("Check Balance")
                    if st.button("Check bal"):
                        showbal(accountnumber)

                elif task == "Transfer":
                    st.subheader("Transfer")
            else:
                st.warning("Incorrect Username/Password")
    
    elif choice == "SignUp":
        st.subheader("Create new Account")
        name= st.text_input("Name")
        accountnumber = st.text_input("Phone number")
        password = st.text_input("password",type='password')

        if st.button("SignUp"):
            create_custtable()
            create_accttable()
            add_cust(accountnumber,name,password)
            st.success("You have successfully craeated a valid account")
            st.info("Go to Login Menu to login")




if __name__ == '__main__':
    main()