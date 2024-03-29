-- Database Reset:

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;
-- Drop the payments table
DROP TABLE IF EXISTS `payments`;
-- Drop the bookings table
DROP TABLE IF EXISTS `Bookings`;
-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Drop dependent tables
DROP TABLE IF EXISTS `Lessontypes`;
DROP TABLE IF EXISTS `OneOnOneLessons`;
DROP TABLE IF EXISTS `Workshops`;
DROP TABLE IF EXISTS `Subscriptions`;
DROP TABLE IF EXISTS `MemberProfiles`;
DROP TABLE IF EXISTS `TutorProfiles`;
DROP TABLE IF EXISTS `ManagerProfiles`;
DROP TABLE IF EXISTS `Location`;

-- Drop tables with foreign key constraints
DROP TABLE IF EXISTS `Users`;
DROP TABLE IF EXISTS `Roles`;

-- Create Location table
CREATE TABLE Location (
  LocationName VARCHAR(80) NOT NULL PRIMARY KEY,
  Description VARCHAR(400) NULL,
  Available BIT NULL DEFAULT 1
);

insert into Location values 
('Farm A', 'Farm A is located at 7 Rich road', 1),
('Farm B', 'Farm B is located at 7 Rich road', 1),
('Farm C', 'Farm C is located at 7 Rich road', 1),
('Farm D', 'Farm D is located at 7 Rich road', 1),
('Farm E', 'Farm E is located at 7 Rich road', 1),
('Farm F', 'Farm F is located at 7 Rich road', 1),
('Farm G', 'Farm G is located at 7 Rich road', 1),
('Farm H', 'Farm H is located at 7 Rich road', 1),
('Farm I', 'Farm I is located at 7 Rich road', 1),
('Farm J', 'Farm J is located at 7 Rich road', 1),
('Farm K', 'Farm K is located at 7 Rich road', 1),
('Farm L', 'Farm L is located at 7 Rich road', 1),
('Farm M', 'Farm M is located at 7 Rich road', 1),
('Farm N', 'Farm N is located at 7 Rich road', 1),
('Farm O', 'Farm O is located at 7 Rich road', 1),
('Farm P', 'Farm P is located at 7 Rich road', 1),
('Farm Q', 'Farm Q is located at 7 Rich road', 1),
('Farm R', 'Farm R is located at 7 Rich road', 1),
('Farm S', 'Farm S is located at 7 Rich road', 1),
('Farm T', 'Farm T is located at 7 Rich road', 1),
('Online', '', 1);


-- Create Roles table
CREATE TABLE Roles (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    RoleName VARCHAR(50) NOT NULL
);

-- Create Users table
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    RoleID INT,
    CreatedAt DATETIME,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
);

-- Create MemberProfiles table
CREATE TABLE MemberProfiles (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(10),
    FirstName VARCHAR(50),
    FamilyName VARCHAR(50),
    Position VARCHAR(100),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(100),
    Address VARCHAR(255),
    DateOfBirth DATE,
    ProfileImage TEXT,
    MerinoBreedingDetails TEXT,
    SubscriptionID INT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Create TutorProfiles table
CREATE TABLE TutorProfiles (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(10),
    FirstName VARCHAR(50),
    FamilyName VARCHAR(50),
    Position VARCHAR(100),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(100),
    TutorProfile TEXT,
    ProfileImage TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Create ManagerProfiles table
CREATE TABLE ManagerProfiles (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(10),
    FirstName VARCHAR(50),
    FamilyName VARCHAR(50),
    Position VARCHAR(100),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(100),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Subscriptions (
    SubscriptionID INT AUTO_INCREMENT PRIMARY KEY,
    Type ENUM('Annual', 'Monthly'),
    Fee DECIMAL(10,2),
    Discount DECIMAL(10,2),
    StartDate DATE,
    EndDate DATE,
    MemberID INT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subscriptionStatus ENUM('Active', 'Inactive'),
    FOREIGN KEY (MemberID) REFERENCES MemberProfiles(UserID)
);

DELIMITER //
CREATE TRIGGER SetSubscriptionStatus BEFORE INSERT ON Subscriptions
FOR EACH ROW
BEGIN
    IF NEW.StartDate <= CURDATE() AND NEW.EndDate >= CURDATE() THEN
        SET NEW.subscriptionStatus = 'Active';
    ELSE
        SET NEW.subscriptionStatus = 'Inactive';
    END IF;
END;
//
DELIMITER ;

-- Create Lesson Types
CREATE TABLE LessonTypes (
    LessonTypeID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT
);
-- Create Workshops table
CREATE TABLE Workshops (
    WorkshopID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255),
    Details TEXT,
    Location VARCHAR(255),
    Date DATE,
    Time TIME,
    Cost DECIMAL(10,2),
    Capacity INT,
    TutorID INT,
    CreatedAt DATETIME,
    FOREIGN KEY (TutorID) REFERENCES TutorProfiles(UserID)
);

-- Create OneOnOneLessons table
CREATE TABLE OneOnOneLessons (
    LessonID INT AUTO_INCREMENT PRIMARY KEY,
    TutorID INT,
    Date DATE,
    StartTime TIME,
    EndTime TIME,
    Location VARCHAR(255),
    Cost DECIMAL(10,2),
    IsBooked BOOLEAN DEFAULT FALSE,
    LessonTypeID INT,
    CreatedAt DATETIME,
    FOREIGN KEY (TutorID) REFERENCES TutorProfiles(UserID),
    FOREIGN KEY (LessonTypeID) REFERENCES LessonTypes(LessonTypeID)
);

-- Create Bookings table
CREATE TABLE Bookings (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT,
    WorkshopID INT,
    LessonID INT,
    BookingDate DATE,
    CreatedAt DATETIME,
    Status ENUM('Confirmed', 'Cancelled'),
    Note TEXT,
    FOREIGN KEY (MemberID) REFERENCES MemberProfiles(UserID),
    FOREIGN KEY (WorkshopID) REFERENCES Workshops(WorkshopID),
    FOREIGN KEY (LessonID) REFERENCES OneOnOneLessons(LessonID)
);

-- Create Payments table
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    MemberID INT,
    SubscriptionID INT,
    BookingID INT,
    Amount DECIMAL(10,2),
    Date DATE,
    CreatedAt DATETIME,
    Type ENUM('Subscription', 'Workshop', 'Lesson'),
    FOREIGN KEY (MemberID) REFERENCES MemberProfiles(UserID),
    FOREIGN KEY (SubscriptionID) REFERENCES Subscriptions(SubscriptionID),
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID)
);

INSERT INTO Roles (RoleName) VALUES ('Member'), ('Tutor'), ('Manager');
--  Users
INSERT INTO Users (UserID, Username, PasswordHash, RoleID, CreatedAt) VALUES 
(1, 'member01', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(2,'member02', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(3,'member03', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(4,'member04', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(5,'member05', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(6,'member06', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(7,'member07', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(8,'member08', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(9,'member09', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(10,'member10', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(11,'member11', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(12,'member12', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(13,'member13', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(14,'member14', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(15,'member15', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(16,'member16', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(17,'member17', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(18,'member18', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(19,'member19', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(20,'member20', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 1, NOW()),
(21,'tutor01', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 2, NOW()),
(22,'tutor02', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 2, NOW()),
(23,'tutor03', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 2, NOW()),
(24,'tutor04', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 2, NOW()),
(25,'tutor05', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 2, NOW()),
(26,'manager01', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 3, NOW()),
(27,'manager02', 'dbd9a47be978b75a020ed6073088f5c9e686fccbeffa16877d916ad3e173c47b', 3, NOW());

-- MemberProfiles
INSERT INTO MemberProfiles (UserID, Title, FirstName, FamilyName, Position, PhoneNumber, Email, Address, DateOfBirth, ProfileImage, MerinoBreedingDetails) VALUES 
(1, 'Mr.', 'John', 'Doe', 'Farmer', '555-0101', 'john.doe01@email.com', '123 Elm St', '1980-01-01', '', 'Breeds fine Merino sheep'),
(2, 'Ms.', 'Jane', 'Smith', 'Breeder', '555-0102', 'jane.smith02@email.com', '456 Oak St', '1982-02-02', '', 'Specializes in wool quality'),
(3, 'Mr.', 'Jim', 'Brown', 'Farmer', '555-0103', 'jim.brown03@email.com', '789 Pine St', '1984-03-03', '', 'Expert in sustainable farming'),
(4, 'Ms.', 'Jackie', 'Davis', 'Breeder', '555-0104', 'jackie.davis04@email.com', '321 Birch St', '1986-04-04', '', 'Focuses on genetic improvement'),
(5, 'Mr.', 'Jake', 'Wilson', 'Farmer', '555-0105', 'jake.wilson05@email.com', '654 Cedar St', '1988-05-05', '', 'Has a large Merino flock'),
(6, 'Ms.', 'Julia', 'Garcia', 'Breeder', '555-0106', 'julia.garcia06@email.com', '987 Spruce St', '1990-06-06', '', 'Advocate for animal health'),
(7, 'Mr.', 'Jeremy', 'Miller', 'Farmer', '555-0107', 'jeremy.miller07@email.com', '246 Maple St', '1992-07-07', '', 'Specialist in pasture management'),
(8, 'Ms.', 'Jasmine', 'Martinez', 'Breeder', '555-0108', 'jasmine.martinez08@email.com', '135 Poplar St', '1994-08-08', '', 'Works with rare Merino lines'),
(9, 'Mr.', 'James', 'Taylor', 'Farmer', '555-0109', 'james.taylor09@email.com', '864 Willow St', '1996-09-09', '', 'Experienced in international sales'),
(10, 'Ms.', 'Jessica', 'Anderson', 'Breeder', '555-0110', 'jessica.anderson10@email.com', '975 Elm St', '1998-10-10', '', 'Develops eco-friendly practices'),
(11, 'Mr.', 'Jeff', 'Thomas', 'Farmer', '555-0111', 'jeff.thomas11@email.com', '111 Elm St', '1980-11-11', '', 'Innovates with Merino breeding tech'),
(12, 'Ms.', 'Joan', 'Hernandez', 'Breeder', '555-0112', 'joan.hernandez12@email.com', '222 Oak St', '1982-12-12', '', 'Focused on wool fineness grades'),
(13, 'Mr.', 'Joe', 'Moore', 'Farmer', '555-0113', 'joe.moore13@email.com', '333 Pine St', '1984-01-13', '', 'Leader in ethical breeding'),
(14, 'Ms.', 'Jill', 'Jackson', 'Breeder', '555-0114', 'jill.jackson14@email.com', '444 Birch St', '1986-02-14', '', 'Engages in community education'),
(15, 'Mr.', 'Jonathan', 'Lee', 'Farmer', '555-0115', 'jonathan.lee15@email.com', '555 Cedar St', '1988-03-15', '', 'Advocates for biodiversity'),
(16, 'Ms.', 'Janet', 'Harris', 'Breeder', '555-0116', 'janet.harris16@email.com', '666 Spruce St', '1990-04-16', '', 'Expert in Merino genetics'),
(17, 'Mr.', 'Jordan', 'Clark', 'Farmer', '555-0117', 'jordan.clark17@email.com', '777 Maple St', '1992-05-17', '', 'Pioneer in organic farming'),
(18, 'Ms.', 'Joy', 'Lewis', 'Breeder', '555-0118', 'joy.lewis18@email.com', '888 Poplar St', '1994-06-18', '', 'Conducts Merino wool research'),
(19, 'Mr.', 'Jason', 'Robinson', 'Farmer', '555-0119', 'jason.robinson19@email.com', '999 Willow St', '1996-07-19', '', 'Specializes in drought-resistant breeds'),
(20, 'Ms.', 'Jenny', 'Walker', 'Breeder', '555-0120', 'jenny.walker20@email.com', '101 Elm St', '1998-08-20', '', 'Focuses on improving fleece weight');

-- TutorProfiles
INSERT INTO TutorProfiles (UserID, Title, FirstName, FamilyName, Position, PhoneNumber, Email, TutorProfile, ProfileImage) VALUES 
(21, 'Dr.', 'Emily', 'Jones', 'Senior Tutor', '555-0201', 'emily.jones21@email.com', 'Expert in Merino genetics and breeding.', '21.jpg'),
(22, 'Mr.', 'Michael', 'Taylor', 'Tutor', '555-0202', 'michael.taylor22@email.com', 'Specializes in sustainable farming practices.', '22.jpg'),
(23, 'Ms.', 'Sarah', 'Wilson', 'Junior Tutor', '555-0203', 'sarah.wilson23@email.com', 'Focuses on wool quality improvement.', '23.jpg'),
(24, 'Dr.', 'Lucas', 'Brown', 'Research Tutor', '555-0204', 'lucas.brown24@email.com', 'Conducts research on Merino health and welfare.', '24.jpg'),
(25, 'Ms.', 'Olivia', 'Martinez', 'Assistant Tutor', '555-0205', 'olivia.martinez25@email.com', 'Engaged in teaching advanced breeding techniques.', '25.jpg');

-- ManagerProfiles
INSERT INTO ManagerProfiles (UserID, Title, FirstName, FamilyName, Position, PhoneNumber, Email) VALUES 
(26, 'Mr.', 'Chris', 'Wilson', 'Head Manager', '555-0301', 'chris.wilson26@email.com'),
(27, 'Ms.', 'Patricia', 'Lee', 'Operations Manager', '555-0302', 'patricia.lee27@email.com');


INSERT INTO Subscriptions (MemberID, Type, Fee, Discount, StartDate, EndDate, createdAt, subscriptionStatus) VALUES
(1, 'Annual', 50.00, 0, '2024-01-01', '2024-12-31', CURRENT_TIMESTAMP, NULL),
(2, 'Annual', 50.00, 15.00, '2024-02-01', '2024-12-31', CURRENT_TIMESTAMP, NULL),
(3, 'Monthly', 5.00, 0, '2024-03-01', '2024-03-31', CURRENT_TIMESTAMP, NULL),
(4, 'Monthly', 5.00, 0, '2024-02-15', '2024-03-14', CURRENT_TIMESTAMP, NULL),
(5, 'Annual', 50.00, 15.00, '2024-01-01', '2024-12-31', CURRENT_TIMESTAMP, NULL),
(6, 'Annual', 50.00, 0, '2024-03-01', '2025-02-28', CURRENT_TIMESTAMP, NULL),
(7, 'Annual', 50.00, 0, '2024-01-15', '2025-01-14', CURRENT_TIMESTAMP, NULL),
(8, 'Annual', 50.00, 15.00, '2024-02-01', '2025-01-31', CURRENT_TIMESTAMP, NULL),
(9, 'Annual', 50.00, 0, '2024-03-15', '2025-03-14', CURRENT_TIMESTAMP, NULL),
(10, 'Monthly', 5.00, 0, '2024-03-01', '2024-03-31', CURRENT_TIMESTAMP, NULL),
(11, 'Annual', 50.00, 15.00, '2024-01-01', '2024-12-31', CURRENT_TIMESTAMP, NULL),
(12, 'Annual', 50.00, 0, '2024-03-01', '2025-02-28', CURRENT_TIMESTAMP, NULL),
(13, 'Annual', 50.00, 0, '2024-01-15', '2025-01-14', CURRENT_TIMESTAMP, NULL),
(14, 'Annual', 50.00, 15.00, '2024-02-01', '2025-01-31', CURRENT_TIMESTAMP, NULL),
(15, 'Annual', 50.00, 0, '2024-03-15', '2025-03-14', CURRENT_TIMESTAMP, NULL),
(16, 'Monthly', 5.00, 0, '2024-03-01', '2024-03-31', CURRENT_TIMESTAMP, NULL),
(17, 'Annual', 50.00, 15.00, '2024-01-01', '2024-12-31', CURRENT_TIMESTAMP, NULL),
(18, 'Annual', 50.00, 0, '2024-03-01', '2025-02-28', CURRENT_TIMESTAMP, NULL),
(19, 'Annual', 50.00, 0, '2023-01-15', '2024-01-14', CURRENT_TIMESTAMP, NULL),
(20, 'Annual', 50.00, 15.00, '2024-02-01', '2025-01-31', CURRENT_TIMESTAMP, NULL);


INSERT INTO Workshops (Title, Details, Location, Date, Time, Cost, Capacity, TutorID, CreatedAt) VALUES 
('Merino Genetics Workshop', 'Understanding the genetics behind Merino sheep.', 'Farm A', '2024-04-01', '10:00:00', 200.00, 20, 21, NOW()),
('Sustainable Farming Practices', 'Practices for sustainable Merino sheep farming.', 'Farm B', '2024-04-15', '11:00:00', 150.00, 15, 22, NOW()),
('Wool Quality Improvement', 'Improving the quality of Merino wool through breeding.', 'Farm C', '2024-05-01', '09:00:00', 180.00, 10, 23, NOW()),
('Advanced Breeding Techniques', 'Advanced techniques for breeding Merino sheep.', 'Farm D', '2024-05-15', '14:00:00', 220.00, 25, 24, NOW()),
('Merino Health and Welfare', 'Ensuring the health and welfare of your Merino flock.', 'Farm E', '2024-06-01', '13:00:00', 150.00, 30, 25, NOW()),
('Pasture Management for Merino', 'Effective pasture management strategies for Merino sheep.', 'Farm F', '2024-06-15', '10:00:00', 170.00, 20, 21, NOW()),
('Merino Flock Management', 'Comprehensive flock management for Merino sheep.', 'Farm G', '2024-07-01', '09:00:00', 160.00, 15, 22, NOW()),
('Genetic Improvement Strategies', 'Strategies for genetic improvement in Merino sheep.', 'Farm H', '2024-07-15', '14:00:00', 210.00, 10, 23, NOW()),
('Eco-friendly Farming with Merino', 'Eco-friendly practices for Merino sheep farming.', 'Farm I', '2024-08-01', '11:00:00', 190.00, 25, 24, NOW()),
('International Sales of Merino Wool', 'Expanding your market: International sales of Merino wool.', 'Farm J', '2024-08-15', '13:00:00', 200.00, 30, 25, NOW()),
('Merino Sheep in Cold Climates', 'Managing Merino sheep in colder climates effectively.', 'Farm K', '2024-09-01', '10:00:00', 160.00, 20, 21, NOW()),
('Breeding Tech Innovations for Merino', 'Latest technological innovations in Merino breeding.', 'Farm L', '2024-09-15', '09:00:00', 220.00, 15, 22, NOW()),
('Wool Fineness Grading Workshop', 'Understanding and improving wool fineness grades.', 'Farm M', '2024-10-01', '14:00:00', 180.00, 10, 23, NOW()),
('Ethical Breeding Practices', 'Adopting ethical breeding practices for Merino sheep.', 'Farm N', '2024-10-15', '11:00:00', 150.00, 25, 24, NOW()),
('Community Education on Merino Farming', 'Engaging the community in Merino sheep farming education.', 'Farm O', '2024-11-01', '13:00:00', 170.00, 30, 25, NOW()),
('Biodiversity in Merino Breeding', 'Promoting biodiversity in Merino sheep breeding.', 'Farm P', '2024-11-15', '10:00:00', 200.00, 20, 21, NOW()),
('Merino Genetics and Wool Quality', 'Linking genetics to wool quality in Merino sheep.', 'Farm Q', '2024-12-01', '09:00:00', 190.00, 15, 22, NOW()),
('Organic Farming for Merino Sheep', 'Principles of organic farming applied to Merino sheep.', 'Farm R', '2024-12-15', '14:00:00', 210.00, 10, 23, NOW()),
('Merino Wool Research and Development', 'Current research and development in Merino wool.', 'Farm S', '2025-01-01', '11:00:00', 180.00, 25, 24, NOW()),
('Improving Fleece Weight in Merino', 'Techniques for improving fleece weight in Merino sheep.', 'Farm T', '2025-01-15', '13:00:00', 160.00, 30, 25, NOW());


INSERT INTO LessonTypes (LessonTypeID, Name, Description) VALUES
(1, 'Merino Genetics', 'Understanding the genetics behind Merino sheep, focusing on breeding strategies for wool quality and health.'),
(2, 'Pasture Management', 'Techniques for managing pastures to provide optimal nutrition for Merino sheep, including rotation and sustainable practices.'),
(3,'Sheep Health and Welfare', 'Comprehensive insights into maintaining the health and welfare of Merino sheep, covering common diseases, prevention, and treatment.'),
(4,'Wool Classing and Grading', 'Skills for classing and grading Merino wool, understanding market demands, and improving wool quality.'),
(5,'Business Management for Farmers', 'Guidance on managing a Merino breeding business, including marketing, sales strategies, and financial planning.'),
(6,'Open Consultation', 'Designed for new members with little to no prior experience in Merino sheep farming, covering basics across various subjects.');

INSERT INTO OneOnOneLessons (TutorID, LessonTypeID, Date, StartTime, EndTime, IsBooked, Location, Cost) VALUES 
(21, 1, '2024-05-05', '09:00', '10:00', FALSE, 'Online', 100.00),
(21, 2, '2024-05-06', '11:00', '12:00', FALSE, 'Online', 100.00),
(22, 3, '2024-05-07', '13:00', '14:00', FALSE, 'Online', 100.00),
(22, 4, '2024-05-08', '15:00', '16:00', FALSE, 'Online', 100.00),
(23, 5, '2024-05-09', '09:00', '10:00', FALSE, 'Online', 100.00),
(23, 1, '2024-05-10', '11:00', '12:00', FALSE, 'Online', 100.00),
(24, 2, '2024-05-11', '13:00', '14:00', FALSE, 'Online', 100.00),
(24, 3, '2024-05-12', '15:00', '16:00', FALSE, 'Online', 100.00),
(25, 4, '2024-05-13', '09:00', '10:00', FALSE, 'Online', 100.00),
(25, 5, '2024-05-14', '11:00', '12:00', FALSE, 'Online', 100.00),
(21, 1, '2024-05-15', '13:00', '14:00', FALSE, 'Online', 100.00),
(21, 2, '2024-05-16', '15:00', '16:00', FALSE, 'Online', 100.00),
(22, 3, '2024-05-17', '09:00', '10:00', FALSE, 'Online', 100.00),
(22, 4, '2024-05-18', '11:00', '12:00', FALSE, 'Online', 100.00),
(23, 5, '2024-05-19', '13:00', '14:00', FALSE, 'Online', 100.00),
(23, 1, '2024-05-20', '15:00', '16:00', FALSE, 'Online', 100.00),
(24, 2, '2024-05-21', '09:00', '10:00', FALSE, 'Online', 100.00),
(24, 3, '2024-05-22', '11:00', '12:00', FALSE, 'Online', 100.00),
(25, 4, '2024-05-23', '13:00', '14:00', FALSE, 'Online', 100.00),
(25, 5, '2024-05-24', '15:00', '16:00', FALSE, 'Online', 100.00);




-- Bookings for Workshops
INSERT INTO Bookings (MemberID, WorkshopID, LessonID, BookingDate, Status, CreatedAt) VALUES 
(1, 1, NULL, '2024-04-01', 'Confirmed', NOW()),
(2, 2, NULL, '2024-04-15', 'Confirmed', NOW()),
(3, 3, NULL, '2024-05-01', 'Confirmed', NOW()),
(4, 4, NULL, '2024-05-15', 'Confirmed', NOW()),
(5, 5, NULL, '2024-06-01', 'Confirmed', NOW()),
(6, 6, NULL, '2024-06-15', 'Confirmed', NOW()),
(7, 7, NULL, '2024-07-01', 'Confirmed', NOW()),
(8, 8, NULL, '2024-07-15', 'Confirmed', NOW()),
(9, 9, NULL, '2024-08-01', 'Confirmed', NOW()),
(10, 10, NULL, '2024-08-15', 'Confirmed', NOW());

-- Bookings for OneOnOneLessons
INSERT INTO Bookings (MemberID, WorkshopID, LessonID, BookingDate, Status, CreatedAt) VALUES 
(11, NULL, 1, '2024-05-05', 'Confirmed', NOW()),
(12, NULL, 2, '2024-05-06', 'Confirmed', NOW()),
(13, NULL, 3, '2024-05-07', 'Confirmed', NOW()),
(14, NULL, 4, '2024-05-08', 'Confirmed', NOW()),
(15, NULL, 5, '2024-05-09', 'Confirmed', NOW()),
(16, NULL, 6, '2024-05-10', 'Confirmed', NOW()),
(17, NULL, 7, '2024-05-11', 'Confirmed', NOW()),
(18, NULL, 8, '2024-05-12', 'Confirmed', NOW()),
(19, NULL, 9, '2024-05-13', 'Confirmed', NOW()),
(20, NULL, 10, '2024-05-14', 'Confirmed', NOW());

-- Payments for Subscriptions
INSERT INTO Payments (MemberID, SubscriptionID, BookingID, Amount, Date, Type, CreatedAt) VALUES 
(1, 1, NULL, 50.00, '2024-01-01', 'Subscription', NOW()),
(2, 2, NULL, 35.00, '2024-02-01', 'Subscription', NOW()),
(3, 3, NULL, 50.00, '2024-03-01', 'Subscription', NOW()),
(4, 4, NULL, 50.00, '2024-02-15', 'Subscription', NOW()),
(5, 5, NULL, 35.00, '2024-01-01', 'Subscription', NOW()),
(6, 6, NULL, 50.00, '2024-03-01', 'Subscription', NOW()),
(7, 7, NULL, 50.00, '2024-01-15', 'Subscription', NOW()),
(8, 8, NULL, 35.00, '2024-02-01', 'Subscription', NOW()),
(9, 9, NULL, 50.00, '2024-03-15', 'Subscription', NOW()),
(10, 10, NULL, 50.00, '2024-03-01', 'Subscription', NOW()),
(11, 11, NULL, 35.00, '2024-01-01', 'Subscription', NOW()),
(12, 12, NULL, 50.00, '2024-03-01', 'Subscription', NOW()),
(13, 13, NULL, 50.00, '2024-01-15', 'Subscription', NOW()),
(14, 14, NULL, 35.00, '2024-02-01', 'Subscription', NOW()),
(15, 15, NULL, 50.00, '2024-03-15', 'Subscription', NOW()),
(16, 16, NULL, 50.00, '2024-03-01', 'Subscription', NOW()),
(17, 17, NULL, 35.00, '2024-01-01', 'Subscription', NOW()),
(18, 18, NULL, 5.00, '2024-03-01', 'Subscription', NOW()),
(19, 19, NULL, 5.00, '2024-01-15', 'Subscription', NOW()),
(20, 20, NULL, 5.00, '2024-02-01', 'Subscription', NOW());


-- Payments for Workshop Bookings
INSERT INTO Payments (MemberID, SubscriptionID, BookingID, Amount, Date, Type, CreatedAt) VALUES 
(1, NULL, 1, 200.00, '2023-02-27', 'Workshop', NOW()),
(2, NULL, 2, 150.00, '2023-03-13', 'Workshop', NOW()),
(3, NULL, 3, 180.00, '2023-03-30', 'Workshop', NOW()),
(4, NULL, 4, 220.00, '2023-04-13', 'Workshop', NOW()),
(5, NULL, 5, 150.00, '2023-04-29', 'Workshop', NOW()),
(6, NULL, 6, 170.00, '2023-05-14', 'Workshop', NOW()),
(7, NULL, 7, 160.00, '2023-05-30', 'Workshop', NOW()),
(8, NULL, 8, 210.00, '2023-06-13', 'Workshop', NOW()),
(9, NULL, 9, 190.00, '2023-06-29', 'Workshop', NOW()),
(10, NULL, 10, 200.00, '2023-07-13', 'Workshop', NOW());

-- Payments for Lesson Bookings
INSERT INTO Payments (MemberID, SubscriptionID, BookingID, Amount, Date, Type, CreatedAt) VALUES 
(11, NULL, 11, 100.00, '2023-03-03', 'Lesson', NOW()),
(12, NULL, 12, 100.00, '2023-03-18', 'Lesson', NOW()),
(13, NULL, 13, 100.00, '2023-04-03', 'Lesson', NOW()),
(14, NULL, 14, 100.00, '2023-04-18', 'Lesson', NOW()),
(15, NULL, 15, 100.00, '2023-05-03', 'Lesson', NOW());
