from backend.auth.repositories import UserRepository
from backend.auth.services import AuthService
from backend.blog.repositories import PostRepository
from backend.blog.services import BlogService


user_repository = UserRepository()
post_repository = PostRepository()

auth_service = AuthService()
blog_service = BlogService()
