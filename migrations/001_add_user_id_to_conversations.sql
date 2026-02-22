-- Migration: Add user_id to conversations table
-- Run this SQL manually against your MySQL database

-- Step 1: Add the column (nullable initially)
ALTER TABLE conversations ADD COLUMN user_id INT;

-- Step 2: Assign existing conversations to admin user (id=1)
UPDATE conversations SET user_id = 1;

-- Step 3: Add index for performance
ALTER TABLE conversations ADD INDEX idx_conversations_user_id (user_id);

-- Step 4: Add foreign key constraint
ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user_id
    FOREIGN KEY (user_id) REFERENCES users(id);

-- Note: user_id is kept nullable in the model for backwards compatibility
-- New conversations will always have user_id set
