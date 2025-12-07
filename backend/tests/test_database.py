"""
Tests for database models and operations
"""
import pytest
from datetime import datetime
from models.chat import Chat, Message
from models.user import User

class TestDatabaseModels:
    """Test database models"""
    
    def test_create_chat(self, db_session):
        """Test creating a chat"""
        chat = Chat(title="Test Chat")
        db_session.add(chat)
        db_session.commit()
        
        assert chat.id is not None
        assert chat.title == "Test Chat"
        assert chat.created_at is not None
    
    def test_create_message(self, db_session):
        """Test creating a message"""
        # Create chat first
        chat = Chat(title="Test Chat")
        db_session.add(chat)
        db_session.commit()
        
        # Create message
        message = Message(
            chat_id=chat.id,
            role="user",
            content="Test message"
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.chat_id == chat.id
        assert message.role == "user"
        assert message.content == "Test message"
    
    def test_chat_message_relationship(self, db_session):
        """Test chat-message relationship"""
        chat = Chat(title="Test Chat")
        db_session.add(chat)
        db_session.commit()
        
        message1 = Message(chat_id=chat.id, role="user", content="Message 1")
        message2 = Message(chat_id=chat.id, role="assistant", content="Message 2")
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Test relationship
        assert len(chat.messages) == 2
        assert message1.chat.id == chat.id
        assert message2.chat.id == chat.id
    
    def test_chat_cascade_delete(self, db_session):
        """Test that deleting a chat deletes its messages"""
        chat = Chat(title="Test Chat")
        db_session.add(chat)
        db_session.commit()
        
        message = Message(chat_id=chat.id, role="user", content="Test")
        db_session.add(message)
        db_session.commit()
        
        chat_id = chat.id
        message_id = message.id
        
        # Delete chat
        db_session.delete(chat)
        db_session.commit()
        
        # Verify message is also deleted
        deleted_message = db_session.query(Message).filter(Message.id == message_id).first()
        assert deleted_message is None
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.credits == 0

