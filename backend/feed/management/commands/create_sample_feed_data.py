from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from feed.models import Post, Comment, PostLike, Hashtag, Notification
from jobs.models import Job

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the social feed system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of posts to create',
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=50,
            help='Number of comments to create',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample feed data...'))
        
        # Get users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create some users first.'))
            return
        
        jobs = list(Job.objects.all())
        
        # Sample post content
        sample_posts = [
            {
                'content': "🚀 Excited to share that I've just completed a major project on AI-driven analytics! The insights we've uncovered are game-changing for our industry. #AI #Analytics #Innovation",
                'post_type': 'text',
                'hashtags': ['ai', 'analytics', 'innovation', 'technology']
            },
            {
                'content': "Just attended an amazing tech conference! The future of remote work looks incredibly promising. Here are my key takeaways... #RemoteWork #TechConference #Future",
                'post_type': 'text',
                'hashtags': ['remotework', 'techconference', 'future', 'networking']
            },
            {
                'content': "Sharing an insightful article about sustainable business practices in 2024. Every company should consider implementing these strategies. #Sustainability #Business #GreenTech",
                'post_type': 'article',
                'article_title': 'Sustainable Business Practices for 2024',
                'article_url': 'https://example.com/sustainable-business-2024',
                'article_description': 'A comprehensive guide to implementing sustainable practices in modern businesses.',
                'hashtags': ['sustainability', 'business', 'greentech']
            },
            {
                'content': "Thrilled to announce our team's recognition for outstanding innovation in digital transformation! 🏆 Proud of everyone's hard work. #Achievement #Innovation #TeamWork",
                'post_type': 'achievement',
                'hashtags': ['achievement', 'innovation', 'teamwork', 'success']
            },
            {
                'content': "Great networking event last night! Met so many inspiring professionals working on cutting-edge projects. Love this community! #Networking #Professional #Community",
                'post_type': 'text',
                'hashtags': ['networking', 'professional', 'community', 'inspiration']
            },
            {
                'content': "Looking for talented developers to join our growing team! We're building the next generation of fintech solutions. #Hiring #Developer #Fintech #Opportunity",
                'post_type': 'text',
                'hashtags': ['hiring', 'developer', 'fintech', 'opportunity']
            },
            {
                'content': "Just published a deep dive into machine learning trends for 2024. The convergence of AI and edge computing is fascinating! #MachineLearning #AI #EdgeComputing",
                'post_type': 'article',
                'article_title': 'Machine Learning Trends 2024: AI Meets Edge Computing',
                'article_url': 'https://example.com/ml-trends-2024',
                'article_description': 'Exploring the latest trends in machine learning and edge computing integration.',
                'hashtags': ['machinelearning', 'ai', 'edgecomputing', 'trends']
            },
            {
                'content': "Celebrating 5 years at this amazing company! The journey from startup to industry leader has been incredible. Grateful for this team! 🎉 #Anniversary #Career #Growth",
                'post_type': 'achievement',
                'hashtags': ['anniversary', 'career', 'growth', 'gratitude']
            }
        ]
        
        # Sample comments
        sample_comments = [
            "Congratulations! This is truly inspiring work.",
            "Amazing insights! Thanks for sharing this.",
            "I completely agree with your perspective on this.",
            "This is exactly what our industry needs right now.",
            "Great article! Looking forward to implementing some of these ideas.",
            "Fantastic achievement! Well deserved recognition.",
            "Thanks for sharing your experience. Very valuable!",
            "Inspiring post! Keep up the excellent work.",
            "This resonates so much with my own experience.",
            "Brilliant analysis! Would love to discuss this further.",
        ]
        
        # Create hashtags
        hashtag_names = [
            'ai', 'machinelearning', 'technology', 'innovation', 'startup',
            'career', 'networking', 'business', 'digital', 'transformation',
            'remote', 'work', 'sustainability', 'fintech', 'analytics',
            'leadership', 'team', 'success', 'growth', 'inspiration'
        ]
        
        created_hashtags = {}
        for name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(
                name=name,
                defaults={'posts_count': 0}
            )
            created_hashtags[name] = hashtag
        
        # Create posts
        posts_created = 0
        for i in range(options['posts']):
            post_data = random.choice(sample_posts)
            author = random.choice(users)
            
            # Create post
            post = Post.objects.create(
                author=author,
                content=post_data['content'],
                post_type=post_data['post_type'],
                visibility=random.choice(['public', 'public', 'public', 'connections']),  # Mostly public
                article_title=post_data.get('article_title', ''),
                article_url=post_data.get('article_url', ''),
                article_description=post_data.get('article_description', ''),
                shared_job=random.choice(jobs) if jobs and post_data['post_type'] == 'job_share' else None,
                likes_count=random.randint(0, 50),
                comments_count=random.randint(0, 20),
                shares_count=random.randint(0, 10),
                views_count=random.randint(10, 200),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            
            # Add hashtags
            for hashtag_name in post_data.get('hashtags', []):
                if hashtag_name in created_hashtags:
                    hashtag = created_hashtags[hashtag_name]
                    post.hashtags.add(hashtag)
                    hashtag.posts_count += 1
                    hashtag.save()
            
            # Add some random likes
            num_likes = random.randint(0, min(len(users), 15))
            liked_users = random.sample(users, num_likes)
            for user in liked_users:
                if user != author:  # Don't let users like their own posts
                    PostLike.objects.get_or_create(
                        user=user,
                        post=post,
                        defaults={
                            'reaction_type': random.choice(['like', 'love', 'celebrate', 'support'])
                        }
                    )
            
            posts_created += 1
        
        # Create comments
        posts = list(Post.objects.all())
        comments_created = 0
        
        for i in range(options['comments']):
            post = random.choice(posts)
            author = random.choice([u for u in users if u != post.author])  # Don't comment on own posts always
            content = random.choice(sample_comments)
            
            comment = Comment.objects.create(
                post=post,
                author=author,
                content=content,
                likes_count=random.randint(0, 10),
                replies_count=random.randint(0, 3),
                created_at=timezone.now() - timedelta(days=random.randint(0, 15))
            )
            
            # Create notification for post author
            if post.author != author:
                Notification.objects.create(
                    recipient=post.author,
                    sender=author,
                    notification_type='comment',
                    title=f"{author.full_name} commented on your post",
                    message=f"New comment: {content[:100]}...",
                    post=post,
                    comment=comment,
                    action_url=f"/feed/post/{post.id}/"
                )
            
            comments_created += 1
        
        # Mark some hashtags as trending
        trending_hashtags = random.sample(list(created_hashtags.values()), 5)
        for hashtag in trending_hashtags:
            hashtag.is_trending = True
            hashtag.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {posts_created} posts and {comments_created} comments!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {len(created_hashtags)} hashtags with {len(trending_hashtags)} marked as trending.'
            )
        ) 