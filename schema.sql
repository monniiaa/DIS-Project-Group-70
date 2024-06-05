CREATE TABLE IF NOT EXISTS Users (
    userID SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE ,
    password VARCHAR(50) 
);

CREATE TABLE IF NOT EXISTS Expenses (
    expenseID SERIAL PRIMARY KEY,
    userID INTEGER ,
    name VARCHAR(50),
    amount DECIMAL(10, 2),
    date DATE ,
    category VARCHAR(50) ,
    FOREIGN KEY (userID) REFERENCES Users(userID)
);
-- CREATE TABLE IF NOT EXISTS Categories (
--     categoryID INT PRIMARY KEY,
--     categoryname VARCHAR(255)
-- );

-- CREATE TABLE IF NOT EXISTS BelongTo (
--     expenseID INT,
--     categoryID INT,
--     PRIMARY KEY (expenseID, categoryID),
--     FOREIGN KEY (expenseID) REFERENCES EXPENSES(expenseID),
--     FOREIGN KEY (categoryID) REFERENCES Categories(categoryID)
-- );
