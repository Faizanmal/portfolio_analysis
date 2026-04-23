"""
Personalized Learning & Onboarding System
==========================================

AI-powered learning platform for portfolio analysis with:
- AI-powered onboarding that adapts to user knowledge level
- Interactive tutorials with real portfolio examples
- Personalized learning paths based on investment goals
- Gamification with achievements and progress tracking
- Video content integration and learning resources

Progressive disclosure of features to avoid overwhelming new users.
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict


class KnowledgeLevel(Enum):
    """User knowledge levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    READING = "reading"
    INTERACTIVE = "interactive"
    VIDEO = "video"


class ContentType(Enum):
    """Types of learning content"""
    ARTICLE = "article"
    VIDEO = "video"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    TUTORIAL = "tutorial"
    SIMULATION = "simulation"


class AchievementCategory(Enum):
    """Achievement categories"""
    LEARNING = "learning"
    PORTFOLIO = "portfolio"
    TRADING = "trading"
    ENGAGEMENT = "engagement"
    MILESTONE = "milestone"


class BadgeRarity(Enum):
    """Badge rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class LearnerProfile:
    """User's learning profile"""
    user_id: str
    knowledge_level: KnowledgeLevel = KnowledgeLevel.BEGINNER
    learning_style: LearningStyle = LearningStyle.INTERACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    
    # Investment background
    investment_experience_years: int = 0
    primary_goal: str = "general_learning"
    risk_tolerance: str = "moderate"
    
    # Learning progress
    completed_lessons: Set[str] = field(default_factory=set)
    completed_courses: Set[str] = field(default_factory=set)
    quiz_scores: Dict[str, float] = field(default_factory=dict)
    
    # Time and engagement
    total_learning_time_minutes: int = 0
    streak_days: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Achievements
    achievements: Set[str] = field(default_factory=set)
    experience_points: int = 0
    level: int = 1
    
    # Feature unlocks
    unlocked_features: Set[str] = field(default_factory=set)
    
    # Preferences
    preferred_topics: List[str] = field(default_factory=list)
    blocked_topics: List[str] = field(default_factory=list)
    
    # Assessment results
    skill_assessments: Dict[str, float] = field(default_factory=dict)


@dataclass
class Lesson:
    """Individual lesson content"""
    lesson_id: str
    course_id: str
    title: str
    description: str
    content_type: ContentType
    difficulty: KnowledgeLevel
    
    # Content
    content: str
    video_url: Optional[str] = None
    interactive_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Learning objectives
    learning_objectives: List[str] = field(default_factory=list)
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)
    
    # Metadata
    duration_minutes: int = 10
    xp_reward: int = 50
    order: int = 0
    
    # Quiz
    quiz_questions: List[Dict[str, Any]] = field(default_factory=list)
    passing_score: float = 0.7


@dataclass
class Course:
    """Learning course containing multiple lessons"""
    course_id: str
    title: str
    description: str
    category: str
    difficulty: KnowledgeLevel
    
    # Lessons
    lessons: List[str] = field(default_factory=list)
    
    # Metadata
    duration_minutes: int = 60
    xp_reward: int = 500
    
    # Requirements
    prerequisites: List[str] = field(default_factory=list)
    
    # Completion badge
    completion_badge_id: Optional[str] = None


@dataclass
class Achievement:
    """Achievement/badge definition"""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: BadgeRarity
    
    # Unlock criteria
    criteria_type: str
    criteria_value: Any
    
    # Rewards
    xp_reward: int = 100
    icon: str = "🏆"
    
    # Hidden achievements
    hidden: bool = False


@dataclass
class LearningPath:
    """Personalized learning path"""
    path_id: str
    user_id: str
    title: str
    goal: str
    
    # Path content
    courses: List[str] = field(default_factory=list)
    current_index: int = 0
    
    # Progress
    started_at: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    progress_percentage: float = 0.0
    
    # Customization
    adaptive: bool = True
    pace: str = "moderate"  # slow, moderate, fast


@dataclass
class OnboardingStep:
    """Onboarding flow step"""
    step_id: str
    title: str
    description: str
    order: int
    
    # Content
    content_type: str  # question, tutorial, feature_intro, assessment
    content: Dict[str, Any] = field(default_factory=dict)
    
    # Conditions
    required: bool = True
    show_if: Optional[Dict[str, Any]] = None
    
    # Actions
    feature_to_unlock: Optional[str] = None


class AssessmentEngine:
    """
    Assesses user knowledge and skill levels.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Assessment questions by topic
        self.assessment_questions = self._load_assessment_questions()
    
    def _load_assessment_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load assessment questions"""
        return {
            "basic_investing": [
                {
                    "question": "What is a stock?",
                    "options": [
                        "A loan you give to a company",
                        "Ownership share in a company",
                        "A type of savings account",
                        "A government bond"
                    ],
                    "correct": 1,
                    "explanation": "A stock represents ownership (equity) in a company."
                },
                {
                    "question": "What does diversification mean in investing?",
                    "options": [
                        "Buying only tech stocks",
                        "Spreading investments across different assets",
                        "Investing all money at once",
                        "Only investing in bonds"
                    ],
                    "correct": 1,
                    "explanation": "Diversification means spreading investments to reduce risk."
                },
                {
                    "question": "What is a dividend?",
                    "options": [
                        "A type of stock",
                        "A fee charged by brokers",
                        "A portion of company profits paid to shareholders",
                        "The price of a stock"
                    ],
                    "correct": 2,
                    "explanation": "Dividends are regular payments made to shareholders from company profits."
                }
            ],
            "technical_analysis": [
                {
                    "question": "What does RSI stand for?",
                    "options": [
                        "Relative Stock Index",
                        "Relative Strength Index",
                        "Real Stock Investment",
                        "Risk-based Stock Indicator"
                    ],
                    "correct": 1,
                    "explanation": "RSI (Relative Strength Index) measures momentum to identify overbought/oversold conditions."
                },
                {
                    "question": "What is a moving average used for?",
                    "options": [
                        "Calculating dividends",
                        "Smoothing price data to identify trends",
                        "Measuring company profits",
                        "Calculating interest rates"
                    ],
                    "correct": 1,
                    "explanation": "Moving averages smooth out price data to reveal underlying trends."
                }
            ],
            "risk_management": [
                {
                    "question": "What is the Sharpe Ratio?",
                    "options": [
                        "The ratio of stocks to bonds",
                        "A measure of risk-adjusted returns",
                        "The ratio of dividends to price",
                        "A measure of company debt"
                    ],
                    "correct": 1,
                    "explanation": "Sharpe Ratio measures returns relative to risk taken."
                },
                {
                    "question": "What does 'VaR' stand for in risk management?",
                    "options": [
                        "Variable Asset Return",
                        "Value at Risk",
                        "Volatile Asset Ratio",
                        "Virtual Asset Reserve"
                    ],
                    "correct": 1,
                    "explanation": "VaR (Value at Risk) estimates potential losses over a given period."
                }
            ]
        }
    
    async def assess_user(self, user_id: str) -> Dict[str, Any]:
        """Run initial assessment for user"""
        # Collect questions from each category
        questions = []
        for topic, topic_questions in self.assessment_questions.items():
            for q in topic_questions[:2]:  # 2 questions per topic
                questions.append({**q, "topic": topic})
        
        return {
            "assessment_id": secrets.token_urlsafe(16),
            "user_id": user_id,
            "questions": questions,
            "total_questions": len(questions)
        }
    
    async def evaluate_assessment(
        self,
        user_id: str,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate assessment answers"""
        scores_by_topic = defaultdict(list)
        total_correct = 0
        
        for answer in answers:
            topic = answer.get("topic", "general")
            is_correct = answer.get("selected") == answer.get("correct")
            scores_by_topic[topic].append(1.0 if is_correct else 0.0)
            if is_correct:
                total_correct += 1
        
        # Calculate scores
        topic_scores = {
            topic: sum(scores) / len(scores) if scores else 0.0
            for topic, scores in scores_by_topic.items()
        }
        
        overall_score = total_correct / len(answers) if answers else 0.0
        
        # Determine knowledge level
        if overall_score >= 0.9:
            level = KnowledgeLevel.EXPERT
        elif overall_score >= 0.7:
            level = KnowledgeLevel.ADVANCED
        elif overall_score >= 0.5:
            level = KnowledgeLevel.INTERMEDIATE
        else:
            level = KnowledgeLevel.BEGINNER
        
        return {
            "overall_score": overall_score,
            "topic_scores": topic_scores,
            "suggested_level": level.value,
            "weak_areas": [t for t, s in topic_scores.items() if s < 0.5],
            "strong_areas": [t for t, s in topic_scores.items() if s >= 0.8]
        }


class OnboardingManager:
    """
    Manages user onboarding flow.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Onboarding steps
        self.onboarding_steps = self._create_onboarding_flow()
        
        # User progress
        self.user_progress: Dict[str, Dict[str, Any]] = {}
    
    def _create_onboarding_flow(self) -> List[OnboardingStep]:
        """Create onboarding flow steps"""
        return [
            OnboardingStep(
                step_id="welcome",
                title="Welcome to Portfolio Analysis",
                description="Let's set up your personalized experience",
                order=0,
                content_type="tutorial",
                content={
                    "message": "Welcome! I'm your AI assistant. Let me help you get started with portfolio analysis and investing.",
                    "image": "/assets/welcome.png"
                }
            ),
            OnboardingStep(
                step_id="experience_level",
                title="Your Investment Experience",
                description="Help us understand your background",
                order=1,
                content_type="question",
                content={
                    "question": "How would you describe your investment experience?",
                    "options": [
                        {"value": "beginner", "label": "I'm new to investing", "icon": "🌱"},
                        {"value": "intermediate", "label": "I have some experience", "icon": "📈"},
                        {"value": "advanced", "label": "I'm an experienced investor", "icon": "💹"},
                        {"value": "expert", "label": "I'm a professional", "icon": "🎯"}
                    ]
                }
            ),
            OnboardingStep(
                step_id="investment_goal",
                title="Your Investment Goals",
                description="What are you looking to achieve?",
                order=2,
                content_type="question",
                content={
                    "question": "What's your primary investment goal?",
                    "options": [
                        {"value": "retirement", "label": "Retirement savings", "icon": "🏖️"},
                        {"value": "growth", "label": "Wealth growth", "icon": "📊"},
                        {"value": "income", "label": "Regular income", "icon": "💰"},
                        {"value": "trading", "label": "Active trading", "icon": "⚡"}
                    ]
                }
            ),
            OnboardingStep(
                step_id="risk_tolerance",
                title="Risk Tolerance",
                description="How do you feel about investment risk?",
                order=3,
                content_type="question",
                content={
                    "question": "How would you react to a 20% drop in your portfolio?",
                    "options": [
                        {"value": "conservative", "label": "I'd sell immediately", "icon": "🛡️"},
                        {"value": "moderate", "label": "I'd be concerned but hold", "icon": "⚖️"},
                        {"value": "aggressive", "label": "I'd see it as a buying opportunity", "icon": "🚀"}
                    ]
                }
            ),
            OnboardingStep(
                step_id="initial_assessment",
                title="Quick Knowledge Check",
                description="Let's see where you're starting from",
                order=4,
                content_type="assessment",
                content={
                    "message": "Answer a few questions to personalize your learning path.",
                    "question_count": 5
                }
            ),
            OnboardingStep(
                step_id="portfolio_tour",
                title="Portfolio Dashboard Tour",
                description="Learn the key features",
                order=5,
                content_type="feature_intro",
                content={
                    "features": [
                        {
                            "name": "Portfolio Overview",
                            "description": "See all your holdings at a glance",
                            "highlight_element": "#portfolio-overview"
                        },
                        {
                            "name": "Performance Charts",
                            "description": "Track your portfolio's performance over time",
                            "highlight_element": "#performance-chart"
                        },
                        {
                            "name": "AI Insights",
                            "description": "Get intelligent recommendations from our AI",
                            "highlight_element": "#ai-insights"
                        }
                    ]
                },
                feature_to_unlock="basic_portfolio"
            ),
            OnboardingStep(
                step_id="first_analysis",
                title="Your First Analysis",
                description="Let's analyze a stock together",
                order=6,
                content_type="tutorial",
                content={
                    "steps": [
                        {"action": "search", "instruction": "Search for a stock symbol (e.g., AAPL)"},
                        {"action": "view", "instruction": "Review the analysis results"},
                        {"action": "understand", "instruction": "I'll explain what each metric means"}
                    ]
                },
                feature_to_unlock="stock_analysis"
            ),
            OnboardingStep(
                step_id="complete",
                title="You're All Set!",
                description="You've completed the onboarding",
                order=7,
                content_type="tutorial",
                content={
                    "message": "Congratulations! You've completed the setup. Here's your personalized learning path.",
                    "next_steps": [
                        "Explore your portfolio dashboard",
                        "Start your first learning module",
                        "Set up price alerts"
                    ]
                },
                feature_to_unlock="full_access"
            )
        ]
    
    async def start_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Start onboarding for user"""
        self.user_progress[user_id] = {
            "current_step": 0,
            "responses": {},
            "started_at": datetime.now().isoformat(),
            "completed": False
        }
        
        first_step = self.onboarding_steps[0]
        return {
            "step": self._format_step(first_step),
            "progress": 0,
            "total_steps": len(self.onboarding_steps)
        }
    
    async def submit_step(
        self,
        user_id: str,
        step_id: str,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit step response and get next step"""
        progress = self.user_progress.get(user_id, {})
        
        # Save response
        if "responses" not in progress:
            progress["responses"] = {}
        progress["responses"][step_id] = response
        
        # Move to next step
        current_index = progress.get("current_step", 0)
        next_index = current_index + 1
        
        if next_index >= len(self.onboarding_steps):
            progress["completed"] = True
            progress["completed_at"] = datetime.now().isoformat()
            self.user_progress[user_id] = progress
            
            return {
                "completed": True,
                "profile": await self._build_profile_from_responses(user_id, progress["responses"])
            }
        
        progress["current_step"] = next_index
        self.user_progress[user_id] = progress
        
        next_step = self.onboarding_steps[next_index]
        return {
            "step": self._format_step(next_step),
            "progress": next_index / len(self.onboarding_steps),
            "total_steps": len(self.onboarding_steps)
        }
    
    def _format_step(self, step: OnboardingStep) -> Dict[str, Any]:
        """Format step for API response"""
        return {
            "step_id": step.step_id,
            "title": step.title,
            "description": step.description,
            "content_type": step.content_type,
            "content": step.content,
            "required": step.required
        }
    
    async def _build_profile_from_responses(
        self,
        user_id: str,
        responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build learner profile from onboarding responses"""
        experience = responses.get("experience_level", {}).get("value", "beginner")
        goal = responses.get("investment_goal", {}).get("value", "growth")
        risk = responses.get("risk_tolerance", {}).get("value", "moderate")
        
        level_map = {
            "beginner": KnowledgeLevel.BEGINNER,
            "intermediate": KnowledgeLevel.INTERMEDIATE,
            "advanced": KnowledgeLevel.ADVANCED,
            "expert": KnowledgeLevel.EXPERT
        }
        
        return {
            "user_id": user_id,
            "knowledge_level": level_map.get(experience, KnowledgeLevel.BEGINNER).value,
            "primary_goal": goal,
            "risk_tolerance": risk,
            "unlocked_features": ["basic_portfolio", "stock_analysis", "full_access"]
        }


class ContentLibrary:
    """
    Manages learning content library.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Content storage
        self.lessons: Dict[str, Lesson] = {}
        self.courses: Dict[str, Course] = {}
        
        # Initialize content
        self._load_content()
    
    def _load_content(self):
        """Load learning content"""
        # Create courses
        self.courses = {
            "investing_101": Course(
                course_id="investing_101",
                title="Investing 101",
                description="Learn the fundamentals of investing",
                category="fundamentals",
                difficulty=KnowledgeLevel.BEGINNER,
                lessons=["intro_investing", "stocks_basics", "bonds_basics", "diversification", "risk_return"],
                duration_minutes=120,
                xp_reward=500,
                completion_badge_id="investing_graduate"
            ),
            "technical_analysis": Course(
                course_id="technical_analysis",
                title="Technical Analysis Fundamentals",
                description="Learn to read charts and identify patterns",
                category="analysis",
                difficulty=KnowledgeLevel.INTERMEDIATE,
                lessons=["chart_basics", "support_resistance", "moving_averages", "rsi_macd", "patterns"],
                duration_minutes=180,
                xp_reward=750,
                prerequisites=["investing_101"],
                completion_badge_id="chartist"
            ),
            "portfolio_management": Course(
                course_id="portfolio_management",
                title="Portfolio Management",
                description="Build and manage a diversified portfolio",
                category="portfolio",
                difficulty=KnowledgeLevel.INTERMEDIATE,
                lessons=["asset_allocation", "rebalancing", "risk_metrics", "tax_efficiency", "optimization"],
                duration_minutes=150,
                xp_reward=700,
                prerequisites=["investing_101"],
                completion_badge_id="portfolio_master"
            ),
            "ai_trading": Course(
                course_id="ai_trading",
                title="AI-Powered Trading",
                description="Leverage AI for smarter investment decisions",
                category="advanced",
                difficulty=KnowledgeLevel.ADVANCED,
                lessons=["ai_overview", "sentiment_analysis", "predictive_models", "risk_management", "automation"],
                duration_minutes=200,
                xp_reward=1000,
                prerequisites=["technical_analysis", "portfolio_management"],
                completion_badge_id="ai_trader"
            )
        }
        
        # Create lessons
        self.lessons = {
            "intro_investing": Lesson(
                lesson_id="intro_investing",
                course_id="investing_101",
                title="Introduction to Investing",
                description="What is investing and why does it matter?",
                content_type=ContentType.INTERACTIVE,
                difficulty=KnowledgeLevel.BEGINNER,
                content="""# Why Invest?

Investing is the act of putting money to work to grow your wealth over time. Unlike saving, investing involves taking on some risk for potentially higher returns.

## Key Concepts

1. **Compound Growth**: Your returns generate their own returns
2. **Inflation**: Money loses purchasing power over time
3. **Time Horizon**: Longer investments can weather more volatility

## The Power of Compounding

If you invest $1,000 with a 7% annual return:
- After 10 years: $1,967
- After 20 years: $3,870
- After 30 years: $7,612

Starting early makes a huge difference!""",
                learning_objectives=[
                    "Understand why investing matters",
                    "Know the difference between saving and investing",
                    "Grasp the concept of compound growth"
                ],
                duration_minutes=15,
                xp_reward=50,
                order=0,
                quiz_questions=[
                    {
                        "question": "What is compound growth?",
                        "options": [
                            "Growth that compounds annually",
                            "Returns generating their own returns",
                            "A type of savings account",
                            "Tax-deferred growth"
                        ],
                        "correct": 1
                    }
                ]
            ),
            "stocks_basics": Lesson(
                lesson_id="stocks_basics",
                course_id="investing_101",
                title="Understanding Stocks",
                description="Learn what stocks are and how they work",
                content_type=ContentType.INTERACTIVE,
                difficulty=KnowledgeLevel.BEGINNER,
                content="""# What is a Stock?

A stock represents ownership in a company. When you buy shares, you become a partial owner.

## Types of Stocks

1. **Common Stock**: Voting rights, potential dividends
2. **Preferred Stock**: Fixed dividends, priority in bankruptcy
3. **Growth Stocks**: Reinvest profits for growth
4. **Value Stocks**: Undervalued relative to fundamentals

## How Stock Prices Move

Stock prices are determined by supply and demand:
- More buyers → Price goes up
- More sellers → Price goes down

Factors affecting prices:
- Company earnings
- Economic conditions
- Market sentiment
- Industry trends""",
                learning_objectives=[
                    "Understand what stocks represent",
                    "Know different types of stocks",
                    "Understand how prices are determined"
                ],
                prerequisites=["intro_investing"],
                duration_minutes=20,
                xp_reward=60,
                order=1
            )
        }
    
    async def get_course(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        return self.courses.get(course_id)
    
    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson by ID"""
        return self.lessons.get(lesson_id)
    
    async def get_recommended_courses(
        self,
        profile: LearnerProfile
    ) -> List[Course]:
        """Get recommended courses based on profile"""
        recommendations = []
        
        for course in self.courses.values():
            # Check prerequisites
            if not all(p in profile.completed_courses for p in course.prerequisites):
                continue
            
            # Already completed
            if course.course_id in profile.completed_courses:
                continue
            
            # Match difficulty
            if course.difficulty.value <= profile.knowledge_level.value or \
               profile.knowledge_level == KnowledgeLevel.BEGINNER:
                recommendations.append(course)
        
        return recommendations[:5]


class GamificationEngine:
    """
    Handles gamification: achievements, XP, levels, streaks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Achievements
        self.achievements = self._load_achievements()
        
        # Level thresholds
        self.level_thresholds = [
            0, 100, 250, 500, 1000, 1750, 2750, 4000, 5500, 7500,
            10000, 13000, 16500, 20500, 25000, 30000, 36000, 43000, 51000, 60000
        ]
    
    def _load_achievements(self) -> Dict[str, Achievement]:
        """Load achievement definitions"""
        return {
            # Learning achievements
            "first_lesson": Achievement(
                achievement_id="first_lesson",
                name="First Steps",
                description="Complete your first lesson",
                category=AchievementCategory.LEARNING,
                rarity=BadgeRarity.COMMON,
                criteria_type="lessons_completed",
                criteria_value=1,
                xp_reward=50,
                icon="📖"
            ),
            "quick_learner": Achievement(
                achievement_id="quick_learner",
                name="Quick Learner",
                description="Complete 10 lessons",
                category=AchievementCategory.LEARNING,
                rarity=BadgeRarity.UNCOMMON,
                criteria_type="lessons_completed",
                criteria_value=10,
                xp_reward=200,
                icon="🎓"
            ),
            "knowledge_seeker": Achievement(
                achievement_id="knowledge_seeker",
                name="Knowledge Seeker",
                description="Complete a full course",
                category=AchievementCategory.LEARNING,
                rarity=BadgeRarity.RARE,
                criteria_type="courses_completed",
                criteria_value=1,
                xp_reward=500,
                icon="📚"
            ),
            "quiz_master": Achievement(
                achievement_id="quiz_master",
                name="Quiz Master",
                description="Score 100% on 5 quizzes",
                category=AchievementCategory.LEARNING,
                rarity=BadgeRarity.RARE,
                criteria_type="perfect_quizzes",
                criteria_value=5,
                xp_reward=300,
                icon="💯"
            ),
            
            # Portfolio achievements
            "portfolio_builder": Achievement(
                achievement_id="portfolio_builder",
                name="Portfolio Builder",
                description="Analyze your first portfolio",
                category=AchievementCategory.PORTFOLIO,
                rarity=BadgeRarity.COMMON,
                criteria_type="portfolio_analyses",
                criteria_value=1,
                xp_reward=100,
                icon="📊"
            ),
            "diversified": Achievement(
                achievement_id="diversified",
                name="Well Diversified",
                description="Hold 10 or more positions",
                category=AchievementCategory.PORTFOLIO,
                rarity=BadgeRarity.UNCOMMON,
                criteria_type="positions_count",
                criteria_value=10,
                xp_reward=200,
                icon="🌐"
            ),
            
            # Engagement achievements
            "week_streak": Achievement(
                achievement_id="week_streak",
                name="Week Warrior",
                description="Maintain a 7-day learning streak",
                category=AchievementCategory.ENGAGEMENT,
                rarity=BadgeRarity.UNCOMMON,
                criteria_type="streak_days",
                criteria_value=7,
                xp_reward=250,
                icon="🔥"
            ),
            "month_streak": Achievement(
                achievement_id="month_streak",
                name="Dedication",
                description="Maintain a 30-day learning streak",
                category=AchievementCategory.ENGAGEMENT,
                rarity=BadgeRarity.EPIC,
                criteria_type="streak_days",
                criteria_value=30,
                xp_reward=1000,
                icon="🌟"
            ),
            
            # Milestone achievements
            "level_5": Achievement(
                achievement_id="level_5",
                name="Rising Investor",
                description="Reach level 5",
                category=AchievementCategory.MILESTONE,
                rarity=BadgeRarity.UNCOMMON,
                criteria_type="level",
                criteria_value=5,
                xp_reward=200,
                icon="⭐"
            ),
            "level_10": Achievement(
                achievement_id="level_10",
                name="Seasoned Investor",
                description="Reach level 10",
                category=AchievementCategory.MILESTONE,
                rarity=BadgeRarity.RARE,
                criteria_type="level",
                criteria_value=10,
                xp_reward=500,
                icon="🌟"
            )
        }
    
    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP"""
        level = 1
        for i, threshold in enumerate(self.level_thresholds):
            if xp >= threshold:
                level = i + 1
            else:
                break
        return level
    
    def xp_for_next_level(self, current_xp: int) -> int:
        """Calculate XP needed for next level"""
        current_level = self.calculate_level(current_xp)
        if current_level >= len(self.level_thresholds):
            return 0
        return self.level_thresholds[current_level] - current_xp
    
    async def award_xp(self, profile: LearnerProfile, amount: int, reason: str) -> Dict[str, Any]:
        """Award XP to user"""
        old_level = profile.level
        profile.experience_points += amount
        new_level = self.calculate_level(profile.experience_points)
        profile.level = new_level
        
        result = {
            "xp_awarded": amount,
            "reason": reason,
            "total_xp": profile.experience_points,
            "level": new_level,
            "leveled_up": new_level > old_level
        }
        
        if new_level > old_level:
            result["new_level"] = new_level
            result["message"] = f"🎉 Level Up! You're now level {new_level}!"
        
        return result
    
    async def check_achievements(
        self,
        profile: LearnerProfile,
        action: str,
        value: Any
    ) -> List[Achievement]:
        """Check and award applicable achievements"""
        unlocked = []
        
        for achievement in self.achievements.values():
            # Already have it
            if achievement.achievement_id in profile.achievements:
                continue
            
            # Check criteria
            earned = False
            
            if achievement.criteria_type == "lessons_completed":
                earned = len(profile.completed_lessons) >= achievement.criteria_value
            elif achievement.criteria_type == "courses_completed":
                earned = len(profile.completed_courses) >= achievement.criteria_value
            elif achievement.criteria_type == "streak_days":
                earned = profile.streak_days >= achievement.criteria_value
            elif achievement.criteria_type == "level":
                earned = profile.level >= achievement.criteria_value
            
            if earned:
                profile.achievements.add(achievement.achievement_id)
                profile.experience_points += achievement.xp_reward
                unlocked.append(achievement)
        
        return unlocked
    
    async def update_streak(self, profile: LearnerProfile) -> Dict[str, Any]:
        """Update user's learning streak"""
        now = datetime.now()
        last_activity = profile.last_activity
        
        # Calculate days since last activity
        days_diff = (now.date() - last_activity.date()).days
        
        if days_diff == 0:
            # Same day, no change
            return {"streak": profile.streak_days, "maintained": True}
        elif days_diff == 1:
            # Consecutive day, increase streak
            profile.streak_days += 1
            return {"streak": profile.streak_days, "increased": True}
        else:
            # Streak broken
            old_streak = profile.streak_days
            profile.streak_days = 1
            return {"streak": 1, "broken": True, "previous_streak": old_streak}


class LearningPathGenerator:
    """
    Generates personalized learning paths.
    """
    
    def __init__(self, config: Dict[str, Any], content_library: ContentLibrary):
        self.config = config
        self.content_library = content_library
        self.logger = logging.getLogger(__name__)
    
    async def generate_path(self, profile: LearnerProfile) -> LearningPath:
        """Generate personalized learning path"""
        # Determine starting point based on level
        if profile.knowledge_level == KnowledgeLevel.BEGINNER:
            courses = ["investing_101", "portfolio_management"]
        elif profile.knowledge_level == KnowledgeLevel.INTERMEDIATE:
            courses = ["technical_analysis", "portfolio_management"]
        elif profile.knowledge_level == KnowledgeLevel.ADVANCED:
            courses = ["ai_trading"]
        else:
            courses = ["ai_trading"]
        
        # Adjust based on goals
        if profile.primary_goal == "trading":
            if "technical_analysis" not in courses:
                courses.insert(0, "technical_analysis")
        elif profile.primary_goal == "retirement":
            if "portfolio_management" not in courses:
                courses.insert(0, "portfolio_management")
        
        # Calculate estimated completion
        total_duration = sum(
            self.content_library.courses[c].duration_minutes 
            for c in courses if c in self.content_library.courses
        )
        
        path = LearningPath(
            path_id=secrets.token_urlsafe(16),
            user_id=profile.user_id,
            title="Your Personalized Learning Journey",
            goal=profile.primary_goal,
            courses=courses,
            estimated_completion=datetime.now() + timedelta(minutes=total_duration * 3)  # Assuming 1/3 pace
        )
        
        return path


class PersonalizedLearningPlatform:
    """
    Main learning platform integrating all components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.assessment = AssessmentEngine(config)
        self.onboarding = OnboardingManager(config)
        self.content = ContentLibrary(config)
        self.gamification = GamificationEngine(config)
        self.path_generator = LearningPathGenerator(config, self.content)
        
        # User profiles
        self.profiles: Dict[str, LearnerProfile] = {}
    
    async def get_or_create_profile(self, user_id: str) -> LearnerProfile:
        """Get or create learner profile"""
        if user_id not in self.profiles:
            self.profiles[user_id] = LearnerProfile(user_id=user_id)
        return self.profiles[user_id]
    
    async def complete_lesson(
        self,
        user_id: str,
        lesson_id: str,
        quiz_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Mark lesson as complete and award XP"""
        profile = await self.get_or_create_profile(user_id)
        lesson = await self.content.get_lesson(lesson_id)
        
        if not lesson:
            return {"error": "Lesson not found"}
        
        # Already completed
        if lesson_id in profile.completed_lessons:
            return {"message": "Lesson already completed", "xp": 0}
        
        # Mark complete
        profile.completed_lessons.add(lesson_id)
        
        # Award XP
        xp_result = await self.gamification.award_xp(
            profile, lesson.xp_reward, f"Completed lesson: {lesson.title}"
        )
        
        # Record quiz score
        if quiz_score is not None:
            profile.quiz_scores[lesson_id] = quiz_score
        
        # Update streak
        streak_result = await self.gamification.update_streak(profile)
        profile.last_activity = datetime.now()
        
        # Check achievements
        achievements = await self.gamification.check_achievements(
            profile, "lesson_complete", lesson_id
        )
        
        # Check course completion
        course = await self.content.get_course(lesson.course_id)
        course_completed = False
        if course and all(lesson_id in profile.completed_lessons for lesson_id in course.lessons):
            profile.completed_courses.add(course.course_id)
            course_completed = True
            course_xp = await self.gamification.award_xp(
                profile, course.xp_reward, f"Completed course: {course.title}"
            )
            xp_result["course_xp"] = course_xp
        
        return {
            "lesson_completed": lesson_id,
            "xp": xp_result,
            "streak": streak_result,
            "achievements": [
                {"id": a.achievement_id, "name": a.name, "icon": a.icon}
                for a in achievements
            ],
            "course_completed": course_completed,
            "level": profile.level,
            "total_xp": profile.experience_points
        }
    
    async def get_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get learning dashboard data"""
        profile = await self.get_or_create_profile(user_id)
        
        # Calculate progress
        total_lessons = len(self.content.lessons)
        completed_lessons = len(profile.completed_lessons)
        
        # Get recommended courses
        recommendations = await self.content.get_recommended_courses(profile)
        
        # Get learning path
        path = await self.path_generator.generate_path(profile)
        
        return {
            "profile": {
                "level": profile.level,
                "xp": profile.experience_points,
                "xp_for_next_level": self.gamification.xp_for_next_level(profile.experience_points),
                "streak_days": profile.streak_days,
                "knowledge_level": profile.knowledge_level.value
            },
            "progress": {
                "lessons_completed": completed_lessons,
                "total_lessons": total_lessons,
                "courses_completed": len(profile.completed_courses),
                "total_courses": len(self.content.courses),
                "percentage": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            },
            "achievements": {
                "earned": len(profile.achievements),
                "total": len(self.gamification.achievements),
                "recent": list(profile.achievements)[-3:]
            },
            "recommendations": [
                {
                    "course_id": c.course_id,
                    "title": c.title,
                    "description": c.description,
                    "duration": c.duration_minutes,
                    "xp": c.xp_reward
                }
                for c in recommendations
            ],
            "learning_path": {
                "path_id": path.path_id,
                "title": path.title,
                "courses": path.courses,
                "progress": path.progress_percentage
            }
        }
    
    def get_api_routes(self):
        """Get FastAPI routes for learning endpoints"""
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
        
        router = APIRouter(prefix="/learning", tags=["Learning"])
        
        class LessonCompleteRequest(BaseModel):
            lesson_id: str
            quiz_score: Optional[float] = None
        
        class OnboardingStepRequest(BaseModel):
            step_id: str
            response: Dict[str, Any]
        
        @router.get("/dashboard")
        async def get_dashboard(user_id: str = "demo_user"):
            return await self.get_dashboard(user_id)
        
        @router.get("/profile")
        async def get_profile(user_id: str = "demo_user"):
            profile = await self.get_or_create_profile(user_id)
            return {
                "user_id": profile.user_id,
                "level": profile.level,
                "xp": profile.experience_points,
                "knowledge_level": profile.knowledge_level.value,
                "streak_days": profile.streak_days,
                "achievements": list(profile.achievements),
                "completed_lessons": list(profile.completed_lessons),
                "completed_courses": list(profile.completed_courses)
            }
        
        @router.post("/onboarding/start")
        async def start_onboarding(user_id: str = "demo_user"):
            return await self.onboarding.start_onboarding(user_id)
        
        @router.post("/onboarding/step")
        async def submit_onboarding_step(
            request: OnboardingStepRequest,
            user_id: str = "demo_user"
        ):
            return await self.onboarding.submit_step(
                user_id, request.step_id, request.response
            )
        
        @router.get("/courses")
        async def list_courses():
            return {
                "courses": [
                    {
                        "course_id": c.course_id,
                        "title": c.title,
                        "description": c.description,
                        "category": c.category,
                        "difficulty": c.difficulty.value,
                        "duration": c.duration_minutes,
                        "lessons": len(c.lessons),
                        "xp": c.xp_reward
                    }
                    for c in self.content.courses.values()
                ]
            }
        
        @router.get("/courses/{course_id}")
        async def get_course(course_id: str):
            course = await self.content.get_course(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            
            lessons = []
            for lesson_id in course.lessons:
                lesson = await self.content.get_lesson(lesson_id)
                if lesson:
                    lessons.append({
                        "lesson_id": lesson.lesson_id,
                        "title": lesson.title,
                        "description": lesson.description,
                        "duration": lesson.duration_minutes,
                        "xp": lesson.xp_reward
                    })
            
            return {
                "course": {
                    "course_id": course.course_id,
                    "title": course.title,
                    "description": course.description,
                    "difficulty": course.difficulty.value,
                    "duration": course.duration_minutes,
                    "xp": course.xp_reward
                },
                "lessons": lessons
            }
        
        @router.get("/lessons/{lesson_id}")
        async def get_lesson(lesson_id: str):
            lesson = await self.content.get_lesson(lesson_id)
            if not lesson:
                raise HTTPException(status_code=404, detail="Lesson not found")
            
            return {
                "lesson_id": lesson.lesson_id,
                "course_id": lesson.course_id,
                "title": lesson.title,
                "description": lesson.description,
                "content_type": lesson.content_type.value,
                "difficulty": lesson.difficulty.value,
                "content": lesson.content,
                "learning_objectives": lesson.learning_objectives,
                "duration": lesson.duration_minutes,
                "xp": lesson.xp_reward,
                "quiz": lesson.quiz_questions if lesson.quiz_questions else None
            }
        
        @router.post("/lessons/complete")
        async def complete_lesson(
            request: LessonCompleteRequest,
            user_id: str = "demo_user"
        ):
            return await self.complete_lesson(
                user_id, request.lesson_id, request.quiz_score
            )
        
        @router.get("/achievements")
        async def get_achievements(user_id: str = "demo_user"):
            profile = await self.get_or_create_profile(user_id)
            
            achievements = []
            for ach in self.gamification.achievements.values():
                achievements.append({
                    "achievement_id": ach.achievement_id,
                    "name": ach.name,
                    "description": ach.description,
                    "category": ach.category.value,
                    "rarity": ach.rarity.value,
                    "icon": ach.icon,
                    "xp": ach.xp_reward,
                    "earned": ach.achievement_id in profile.achievements
                })
            
            return {"achievements": achievements}
        
        @router.get("/path")
        async def get_learning_path(user_id: str = "demo_user"):
            profile = await self.get_or_create_profile(user_id)
            path = await self.path_generator.generate_path(profile)
            
            return {
                "path_id": path.path_id,
                "title": path.title,
                "goal": path.goal,
                "courses": path.courses,
                "progress": path.progress_percentage,
                "estimated_completion": path.estimated_completion.isoformat() if path.estimated_completion else None
            }
        
        @router.get("/assessment")
        async def get_assessment(user_id: str = "demo_user"):
            return await self.assessment.assess_user(user_id)
        
        @router.post("/assessment/evaluate")
        async def evaluate_assessment(answers: List[Dict[str, Any]], user_id: str = "demo_user"):
            result = await self.assessment.evaluate_assessment(user_id, answers)
            
            # Update profile if needed
            profile = await self.get_or_create_profile(user_id)
            if "suggested_level" in result:
                level_map = {
                    "beginner": KnowledgeLevel.BEGINNER,
                    "intermediate": KnowledgeLevel.INTERMEDIATE,
                    "advanced": KnowledgeLevel.ADVANCED,
                    "expert": KnowledgeLevel.EXPERT
                }
                profile.knowledge_level = level_map.get(
                    result["suggested_level"], KnowledgeLevel.BEGINNER
                )
            
            return result
        
        @router.get("/recommendations")
        async def get_recommendations(user_id: str = "demo_user"):
            profile = await self.get_or_create_profile(user_id)
            courses = await self.content.get_recommended_courses(profile)
            
            return {
                "recommendations": [
                    {
                        "course_id": c.course_id,
                        "title": c.title,
                        "description": c.description,
                        "difficulty": c.difficulty.value,
                        "duration": c.duration_minutes,
                        "xp": c.xp_reward
                    }
                    for c in courses
                ]
            }
        
        return router


# Export main components
__all__ = [
    'PersonalizedLearningPlatform',
    'AssessmentEngine',
    'OnboardingManager',
    'ContentLibrary',
    'GamificationEngine',
    'LearningPathGenerator',
    'KnowledgeLevel',
    'LearningStyle',
    'ContentType',
    'BadgeRarity'
]
