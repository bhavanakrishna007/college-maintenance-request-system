-- ============================================================================
-- Course Code: 24CS305 / CS3106 - DBMS Laboratory
-- Project Title: College Maintenance and Request System
-- Sample Data (DML Script with >= 10 records per major table)
-- ============================================================================

USE college_maintenance_db;

-- 1. Insert Departments (10 records)
INSERT INTO departments (dept_id, dept_name, building, block_no, contact_email, contact_phone) VALUES
(1, 'Computer Science & Engineering', 'Turing Academic Complex', 'Block A', 'cse.dept@college.edu', '044-22500101'),
(2, 'Mechanical Engineering', 'Newton Mechanical Block', 'Block B', 'mech.dept@college.edu', '044-22500102'),
(3, 'Electrical & Electronics', 'Faraday Technology Center', 'Block C', 'eee.dept@college.edu', '044-22500103'),
(4, 'Civil Engineering', 'Visvesvaraya Hall', 'Block D', 'civil.dept@college.edu', '044-22500104'),
(5, 'Electronics & Communication', 'Maxwell Electronics Wing', 'Block E', 'ece.dept@college.edu', '044-22500105'),
(6, 'Information Technology', 'Ada Lovelace Building', 'Block F', 'it.dept@college.edu', '044-22500106'),
(7, 'Biotechnology Department', 'Pasteur Bio Science Wing', 'Block G', 'biotech.dept@college.edu', '044-22500107'),
(8, 'Central Library & Media Center', 'Tagore Knowledge Hub', 'Block L', 'library@college.edu', '044-22500108'),
(9, 'Administrative Block & Registrar', 'Main Administration Tower', 'Admin HQ', 'admin.office@college.edu', '044-22500109'),
(10, 'Student Hostel & Dining Facility', 'Ramanujan Hostel Quad', 'Hostel 1', 'hostel.warden@college.edu', '044-22500110');

-- 2. Insert Users (12 records: Admin, Staff, Students, Technicians)
INSERT INTO users (user_id, username, password_hash, full_name, email, phone, role, dept_id) VALUES
(1, 'admin', 'admin123', 'Dr. Rajesh Sundaram', 'admin@college.edu', '9840123456', 'Admin', 9),
(2, 'abhishek_saji', '252101', 'Prof. Ananya Sharma', 'ananya.cse@college.edu', '9840123457', 'Staff', 1),
(3, 'staff_mech', 'staff123', 'Prof. Vikram Verma', 'vikram.mech@college.edu', '9840123458', 'Staff', 2),
(4, 'staff_eee', 'staff123', 'Prof. Sangeetha Nair', 'sangeetha.eee@college.edu', '9840123459', 'Staff', 3),
(5, 'bhavana', '241141', 'Bhavana', '241141@iiitt.ac.in', '7569845231', 'Student', 1),
(6, 'swapna', '241136', 'Swapna', '241136@iitt.ac.in', '8910272631', 'Student', 5),
(7, 'meghana', '241160', 'Meghana', '241160@iitt.ac.in', '9840123462', 'Student', 6),
(8, 'arundhathi', '241107', 'Arundhathi', '241107@iitt.ac.in', '9840123463', 'Student', 7),
(9, 'tech_murugan', 'tech123', 'Murugan K (Electrician)', 'murugan.tech@college.edu', '9840123464', 'Technician', 3),
(10, 'tech_suresh', 'tech123', 'Suresh Babu (Plumber)', 'suresh.tech@college.edu', '9840123465', 'Technician', 4),
(11, 'tech_karthik', 'tech123', 'Karthik Raja (Network)', 'karthik.tech@college.edu', '9840123466', 'Technician', 1),
(12, 'warden_kumar', 'hostel123', 'Capt. R. Kumar', 'hostel.warden@college.edu', '9840123467', 'Staff', 10);

-- 3. Insert Categories (6 records)
INSERT INTO categories (category_id, category_name, description, default_priority, sla_hours) VALUES
(1, 'Electrical', 'Power failure, short circuits, switchboards, lighting, fans', 'High', 12),
(2, 'Plumbing', 'Pipe leaks, taps, washrooms, flush valves, water supply', 'Medium', 24),
(3, 'HVAC / Air Conditioning', 'Split AC units, centralized chilling plants, ventilation ducting', 'Medium', 36),
(4, 'IT & Networking', 'LAN ports, Wi-Fi routers, projectors, lab switches, cabling', 'High', 8),
(5, 'Carpentry & Furniture', 'Broken desks, lab benches, door latches, window panes', 'Low', 48),
(6, 'Civil & Masonry', 'Tile damage, wall cracks, water seepage, ceiling plaster repair', 'Medium', 72);

-- 4. Insert Technicians (10 records)
INSERT INTO technicians (technician_id, user_id, name, specialization, phone, email, status, hourly_rate) VALUES
(1, 9, 'Murugan K', 'Electrical', '9840123464', 'murugan.tech@college.edu', 'Busy', 180.00),
(2, 10, 'Suresh Babu', 'Plumbing', '9840123465', 'suresh.tech@college.edu', 'Busy', 150.00),
(3, 11, 'Karthik Raja', 'IT & Networking', '9840123466', 'karthik.tech@college.edu', 'Available', 200.00),
(4, NULL, 'Mani Kandhan', 'HVAC / Air Conditioning', '9840123470', 'mani.hvac@college.edu', 'Busy', 220.00),
(5, NULL, 'Gopalakrishnan V', 'Carpentry & Furniture', '9840123471', 'gopal.carpenter@college.edu', 'Available', 160.00),
(6, NULL, 'Dhanasekaran P', 'Civil & Masonry', '9840123472', 'dhana.civil@college.edu', 'Available', 170.00),
(7, NULL, 'Saravanan S', 'Electrical', '9840123473', 'saravanan.elec@college.edu', 'Available', 180.00),
(8, NULL, 'Velmurugan R', 'Plumbing', '9840123474', 'velu.plumb@college.edu', 'Available', 150.00),
(9, NULL, 'Pradeep Kumar', 'IT & Networking', '9840123475', 'pradeep.it@college.edu', 'On-Leave', 210.00),
(10, NULL, 'Natarajan M', 'HVAC / Air Conditioning', '9840123476', 'natarajan.ac@college.edu', 'Available', 220.00);

-- 5. Insert Parts Inventory (12 records)
INSERT INTO parts_inventory (part_id, part_name, category, unit_of_measure, unit_cost, stock_quantity, reorder_level) VALUES
(1, 'Philips 20W LED Batten Tube', 'Electrical', 'pcs', 240.00, 50, 10),
(2, 'Anchor 16A Modular Socket & Switch', 'Electrical', 'pcs', 120.00, 40, 8),
(3, 'Finolex 2.5 sq mm Copper Wire Coil', 'Electrical', 'meter', 35.00, 200, 30),
(4, 'Astral 1/2 inch CPVC Ball Valve', 'Plumbing', 'pcs', 180.00, 25, 5),
(5, 'Jaguar Half-Turn Brass Bib Tap', 'Plumbing', 'pcs', 450.00, 15, 4),
(6, 'Teflon Sealing Tape', 'Plumbing', 'rolls', 25.00, 80, 15),
(7, 'Cat6 UTP Patch Cable (3m)', 'IT & Networking', 'pcs', 150.00, 60, 12),
(8, 'D-Link 8-Port Gigabit Switch', 'IT & Networking', 'pcs', 1250.00, 8, 2),
(9, 'Heavy Duty Hydraulic Door Closer', 'Carpentry & Furniture', 'pcs', 850.00, 12, 3),
(10, 'Stainless Steel Butt Hinges 4 inch', 'Carpentry & Furniture', 'pairs', 90.00, 35, 10),
(11, 'R32 Refrigerant Gas Canister (3kg)', 'HVAC / Air Conditioning', 'kg', 650.00, 14, 4),
(12, 'Ultratech Waterproof Mortar Mix (25kg)', 'Civil & Masonry', 'bag', 380.00, 18, 5);

-- 6. Insert Maintenance Requests (15 records)
-- Workflow stages represented: Reported, Categorized, Assigned, In-Progress, Resolved, Closed
INSERT INTO maintenance_requests (request_id, tracking_code, reported_by_id, category_id, dept_id, location_details, issue_title, issue_description, priority, status, reported_at, resolution_notes, resolved_at) VALUES
(1, 'REQ-2026-0001', 2, 1, 1, 'Turing Block, CS Lab 2, Room 204', 'Ceiling tube lights flickering continuously', 'Three 20W LED fixtures in the front row are flickering, disturbing students during lab hours.', 'Medium', 'Resolved', '2026-10-20 09:30:00', 'Replaced 3 faulty LED batten tubes and checked wire connections.', '2026-10-20 14:15:00'),
(2, 'REQ-2026-0002', 5, 2, 1, 'Turing Block, 2nd Floor Restroom', 'Water leakage from main washbasin faucet', 'Continuous tap leak leading to water stagnation on the floor.', 'High', 'Resolved', '2026-10-21 10:15:00', 'Replaced worn valve spindle and wrapped teflon tape.', '2026-10-21 15:45:00'),
(3, 'REQ-2026-0003', 3, 3, 2, 'Newton Block, CAD/CAM Lab, Room 102', 'Split AC unit blowing room-temperature air', 'AC cooling failed in high performance workstation lab. Ambient temperature reaching 32C.', 'High', 'In-Progress', '2026-10-22 11:00:00', NULL, NULL),
(4, 'REQ-2026-0004', 6, 4, 5, 'Maxwell Wing, Embedded Systems Lab 305', 'Ethernet ports dead on bench 4', 'No link light on RJ45 ports 7 and 8 on workbench 4. Students unable to flash boards.', 'High', 'Assigned', '2026-10-23 08:45:00', NULL, NULL),
(5, 'REQ-2026-0005', 4, 5, 3, 'Faraday Center, Seminar Hall B', 'Auditorium chair armrests broken', 'Four seats have broken armrests and loose screws in the 3rd row.', 'Low', 'Assigned', '2026-10-23 14:00:00', NULL, NULL),
(6, 'REQ-2026-0006', 7, 2, 6, 'Ada Lovelace Block, Ground Floor Water Dispenser', 'Water cooler drain line choked', 'Drainage overflowing near main corridor entrance causing slip hazard.', 'Medium', 'In-Progress', '2026-10-24 09:10:00', NULL, NULL),
(7, 'REQ-2026-0007', 8, 6, 7, 'Pasteur Bio Science Wing, Room 108', 'Wall seepage near microbiology autoclave', 'Damp patch spreading behind autoclave machine.', 'Medium', 'Categorized', '2026-10-24 13:20:00', NULL, NULL),
(8, 'REQ-2026-0008', 2, 1, 1, 'Turing Block, Faculty Cabins 12-14', 'Power socket burnt out on cabin desk', 'Sparks seen when plugging in laptop charger. Needs socket replacement.', 'Emergency', 'Assigned', '2026-10-25 09:00:00', NULL, NULL),
(9, 'REQ-2026-0009', 12, 1, 10, 'Ramanujan Hostel, Block C Corridors', 'Corridor emergency lamps not turning on', 'Emergency backup light fixtures dark during routine test.', 'High', 'Reported', '2026-10-25 11:30:00', NULL, NULL),
(10, 'REQ-2026-0010', 12, 2, 10, 'Ramanujan Hostel, 3rd Floor Bathrooms', 'Low water pressure in shower heads', 'Solar hot water line pressure is too low for upper floors.', 'Medium', 'Reported', '2026-10-25 15:00:00', NULL, NULL),
(11, 'REQ-2026-0011', 1, 4, 9, 'Main Admin Block, Boardroom 401', 'Ceiling projector HDMI & LAN signal loss', 'Boardroom presentation display disconnects intermittently.', 'Medium', 'Reported', '2026-10-26 08:30:00', NULL, NULL),
(12, 'REQ-2026-0012', 3, 5, 2, 'Newton Mechanical Block, Machine Shop 1', 'Main entry fire door hydraulic closer damaged', 'Door slams heavily due to lack of hydraulic resistance.', 'Low', 'Reported', '2026-10-26 10:00:00', NULL, NULL),
(13, 'REQ-2026-0013', 2, 1, 1, 'Turing Block, Server Room A', 'Backup exhaust fan making rattling noise', 'Vibration noise detected on cooling ventilation fan.', 'Medium', 'Reported', '2026-10-26 11:20:00', NULL, NULL),
(14, 'REQ-2026-0014', 5, 4, 1, 'Turing Block, Software Project Lab 3', 'Wi-Fi Access Point offline in north wing', 'SSID drop reported across North Wing computers.', 'High', 'Reported', '2026-10-26 14:00:00', NULL, NULL),
(15, 'REQ-2026-0015', 4, 3, 3, 'Faraday Center, Power Electronics Lab', 'AC thermostat display showing error code E4', 'Compressor tripping after 5 minutes of operation.', 'High', 'Reported', '2026-10-26 15:45:00', NULL, NULL);

-- 7. Insert Assignments (12 records)
INSERT INTO assignments (assignment_id, request_id, technician_id, assigned_by_id, assigned_date, work_start_date, work_end_date, work_notes, work_status) VALUES
(1, 1, 1, 1, '2026-10-20 10:00:00', '2026-10-20 11:00:00', '2026-10-20 14:15:00', 'Defective ballasts removed, installed 3 new LED tubelights.', 'Completed'),
(2, 2, 2, 1, '2026-10-21 10:45:00', '2026-10-21 13:00:00', '2026-10-21 15:45:00', 'Replaced faulty brass bib tap and sealed with teflon tape.', 'Completed'),
(3, 3, 4, 1, '2026-10-22 11:30:00', '2026-10-22 13:15:00', NULL, 'Gas leakage detected on flare nut joint. Brazing and topping up R32 gas.', 'Work-Started'),
(4, 4, 3, 1, '2026-10-23 09:30:00', NULL, NULL, 'Scheduled cable continuity testing and crimping new patch cables.', 'Assigned'),
(5, 5, 5, 1, '2026-10-23 15:00:00', NULL, NULL, 'Procuring matching wooden armrests and mounting fasteners.', 'Assigned'),
(6, 6, 2, 1, '2026-10-24 10:00:00', '2026-10-24 11:30:00', NULL, 'Cleared sediment block from 40mm drain pipe, replacing valve.', 'Work-Started'),
(7, 8, 1, 1, '2026-10-25 09:30:00', NULL, NULL, 'Isolating cabin circuit breaker and replacing 16A modular unit.', 'Assigned'),
(8, 1, 7, 1, '2026-10-20 09:45:00', '2026-10-20 10:00:00', '2026-10-20 10:30:00', 'Initial electrical line inspection conducted.', 'Completed'),
(9, 2, 8, 1, '2026-10-21 10:30:00', '2026-10-21 10:45:00', '2026-10-21 11:15:00', 'Initial pressure test and water line isolation.', 'Completed'),
(10, 3, 10, 1, '2026-10-22 11:15:00', '2026-10-22 12:00:00', '2026-10-22 12:45:00', 'Filter cleaning and indoor unit blower inspection.', 'Completed'),
(11, 4, 9, 1, '2026-10-23 09:00:00', '2026-10-23 09:20:00', '2026-10-23 09:40:00', 'Network switch port traffic and LED verification.', 'Completed'),
(12, 6, 8, 1, '2026-10-24 09:30:00', '2026-10-24 09:50:00', '2026-10-24 10:15:00', 'Secondary trap cleared from debris.', 'Completed');

-- 8. Insert Request Parts Used (15 records)
-- Note: triggers will execute upon insertion to adjust parts_inventory stock quantities!
INSERT INTO request_parts_used (usage_id, request_id, part_id, quantity_used, unit_cost_charged, total_cost, notes) VALUES
(1, 1, 1, 3, 240.00, 720.00, '3 LED battens replaced in CS Lab 2'),
(2, 1, 3, 5, 35.00, 175.00, '5 meters wire replaced for burnt neutral line'),
(3, 2, 5, 1, 450.00, 450.00, 'Jaguar bib tap installed on washbasin 2'),
(4, 2, 6, 2, 25.00, 50.00, 'Teflon tape rolls used for threaded joint seal'),
(5, 3, 11, 2, 650.00, 1300.00, '2kg R32 refrigerant topped up'),
(6, 4, 7, 4, 150.00, 600.00, 'Cat6 patch cables replaced on bench 4'),
(7, 6, 4, 1, 180.00, 180.00, 'Astral ball valve fitted to water cooler inlet'),
(8, 8, 2, 2, 120.00, 240.00, 'Anchor 16A socket and switch replacement'),
(9, 8, 3, 4, 35.00, 140.00, '4 meters internal copper wiring'),
(10, 5, 10, 2, 90.00, 180.00, 'Stainless steel hinges for chair flaps'),
(11, 1, 2, 1, 120.00, 120.00, 'Wall switch replaced in CS Lab 2 control panel'),
(12, 2, 4, 1, 180.00, 180.00, 'CPVC gate valve isolation repair'),
(13, 3, 6, 1, 25.00, 25.00, 'Sealing tape for pressure gauge port'),
(14, 4, 8, 1, 1250.00, 1250.00, 'D-Link 8-port switch replaced in rack'),
(15, 6, 6, 1, 25.00, 25.00, 'Thread sealing tape for cooler drain nipple');
