"""
Real-Time Collaboration Tools
=============================

Enterprise-grade collaboration platform for investment teams with:
- Shared workspaces for investment committees/family offices
- Real-time commenting on positions and strategies
- Decision voting system for group investment choices
- Audit trails for all collaborative decisions
- Role-based permissions (viewer, editor, approver)

Financial decisions are often made in teams - this module facilitates that.
"""

import asyncio
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import hashlib


class Permission(Enum):
    """Workspace permissions"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    TRADE = "trade"
    APPROVE = "approve"
    ADMIN = "admin"


class Role(Enum):
    """Predefined roles with permission sets"""
    VIEWER = "viewer"
    ANALYST = "analyst"
    TRADER = "trader"
    PORTFOLIO_MANAGER = "portfolio_manager"
    RISK_OFFICER = "risk_officer"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"
    OWNER = "owner"


class VoteType(Enum):
    """Types of votes"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"


class DecisionStatus(Enum):
    """Decision status"""
    DRAFT = "draft"
    PENDING_VOTES = "pending_votes"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class CommentType(Enum):
    """Types of comments"""
    GENERAL = "general"
    ANALYSIS = "analysis"
    QUESTION = "question"
    CONCERN = "concern"
    APPROVAL = "approval"
    REJECTION = "rejection"
    REPLY = "reply"


class AuditAction(Enum):
    """Auditable actions"""
    WORKSPACE_CREATED = "workspace_created"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    ROLE_CHANGED = "role_changed"
    DECISION_CREATED = "decision_created"
    VOTE_CAST = "vote_cast"
    DECISION_APPROVED = "decision_approved"
    DECISION_REJECTED = "decision_rejected"
    DECISION_EXECUTED = "decision_executed"
    TRADE_PROPOSED = "trade_proposed"
    TRADE_APPROVED = "trade_approved"
    TRADE_EXECUTED = "trade_executed"
    COMMENT_ADDED = "comment_added"
    DOCUMENT_SHARED = "document_shared"
    SETTINGS_CHANGED = "settings_changed"


# Role to permission mapping
ROLE_PERMISSIONS = {
    Role.VIEWER: {Permission.VIEW},
    Role.ANALYST: {Permission.VIEW, Permission.COMMENT},
    Role.TRADER: {Permission.VIEW, Permission.COMMENT, Permission.EDIT, Permission.TRADE},
    Role.PORTFOLIO_MANAGER: {Permission.VIEW, Permission.COMMENT, Permission.EDIT, Permission.TRADE, Permission.APPROVE},
    Role.RISK_OFFICER: {Permission.VIEW, Permission.COMMENT, Permission.APPROVE},
    Role.COMPLIANCE_OFFICER: {Permission.VIEW, Permission.COMMENT, Permission.APPROVE},
    Role.ADMIN: {Permission.VIEW, Permission.COMMENT, Permission.EDIT, Permission.TRADE, Permission.APPROVE, Permission.ADMIN},
    Role.OWNER: {Permission.VIEW, Permission.COMMENT, Permission.EDIT, Permission.TRADE, Permission.APPROVE, Permission.ADMIN}
}


@dataclass
class WorkspaceMember:
    """Workspace member with role and permissions"""
    user_id: str
    username: str
    display_name: str
    role: Role
    custom_permissions: Set[Permission] = field(default_factory=set)
    added_at: datetime = field(default_factory=datetime.now)
    added_by: str = ""
    last_active: Optional[datetime] = None
    is_active: bool = True
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if member has a specific permission"""
        role_perms = ROLE_PERMISSIONS.get(self.role, set())
        return permission in role_perms or permission in self.custom_permissions


@dataclass
class Workspace:
    """Collaborative workspace for investment teams"""
    workspace_id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # Members
    members: Dict[str, WorkspaceMember] = field(default_factory=dict)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Voting configuration
    voting_config: Dict[str, Any] = field(default_factory=lambda: {
        "approval_threshold": 0.6,
        "min_votes_required": 2,
        "voting_period_hours": 24,
        "require_risk_approval": True,
        "require_compliance_approval": False
    })
    
    # Active status
    is_active: bool = True


@dataclass
class Comment:
    """Comment on a position, strategy, or decision"""
    comment_id: str
    workspace_id: str
    author_id: str
    author_name: str
    comment_type: CommentType
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Context
    target_type: str = ""  # position, strategy, decision, trade
    target_id: str = ""
    parent_comment_id: Optional[str] = None
    
    # Attachments
    attachments: List[Dict[str, str]] = field(default_factory=list)
    
    # Engagement
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    mentions: List[str] = field(default_factory=list)
    
    # Editing
    edited_at: Optional[datetime] = None
    is_deleted: bool = False


@dataclass
class Vote:
    """Vote on a decision"""
    vote_id: str
    decision_id: str
    voter_id: str
    voter_name: str
    voter_role: Role
    vote_type: VoteType
    created_at: datetime = field(default_factory=datetime.now)
    
    # Optional comments
    comment: str = ""
    conditions: List[str] = field(default_factory=list)
    
    # Weight (some roles may have higher voting weight)
    weight: float = 1.0


@dataclass
class Decision:
    """Investment decision requiring group approval"""
    decision_id: str
    workspace_id: str
    title: str
    description: str
    decision_type: str  # trade, rebalance, strategy_change, allocation_change
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # Status
    status: DecisionStatus = DecisionStatus.DRAFT
    
    # Voting
    votes: Dict[str, Vote] = field(default_factory=dict)
    voting_deadline: Optional[datetime] = None
    
    # Requirements
    required_approvers: List[str] = field(default_factory=list)
    min_approval_percentage: float = 0.6
    
    # Decision details
    proposed_actions: List[Dict[str, Any]] = field(default_factory=list)
    expected_impact: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Outcome
    final_result: Optional[str] = None
    executed_at: Optional[datetime] = None
    execution_details: Dict[str, Any] = field(default_factory=dict)
    
    # Comments and discussion
    comments: List[Comment] = field(default_factory=list)
    
    def calculate_approval_percentage(self) -> float:
        """Calculate current approval percentage"""
        if not self.votes:
            return 0.0
        
        total_weight = sum(v.weight for v in self.votes.values() if v.vote_type != VoteType.ABSTAIN)
        approve_weight = sum(
            v.weight for v in self.votes.values()
            if v.vote_type in [VoteType.APPROVE, VoteType.CONDITIONAL]
        )
        
        return approve_weight / total_weight if total_weight > 0 else 0.0


@dataclass
class AuditLogEntry:
    """Audit trail entry"""
    entry_id: str
    workspace_id: str
    action: AuditAction
    actor_id: str
    actor_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Details
    target_type: str = ""
    target_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Before/after for changes
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # IP and device info (for security)
    ip_address: str = ""
    user_agent: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/display"""
        return {
            "entry_id": self.entry_id,
            "workspace_id": self.workspace_id,
            "action": self.action.value,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "timestamp": self.timestamp.isoformat(),
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": self.details
        }


@dataclass
class RealTimeUpdate:
    """Real-time update for WebSocket broadcasting"""
    update_id: str
    workspace_id: str
    update_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    recipients: List[str] = field(default_factory=list)  # Empty = all workspace members


class WorkspaceManager:
    """
    Manages collaborative workspaces for investment teams.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.workspaces: Dict[str, Workspace] = {}
        self.update_queue: asyncio.Queue = asyncio.Queue()
        self.websocket_connections: Dict[str, Set[Any]] = {}  # workspace_id -> connections
    
    async def create_workspace(
        self,
        name: str,
        description: str,
        creator_id: str,
        creator_name: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Workspace:
        """Create a new collaborative workspace"""
        workspace = Workspace(
            workspace_id=secrets.token_urlsafe(16),
            name=name,
            description=description,
            created_by=creator_id,
            settings=settings or {}
        )
        
        # Add creator as owner
        owner = WorkspaceMember(
            user_id=creator_id,
            username=f"user_{creator_id[:8]}",
            display_name=creator_name,
            role=Role.OWNER,
            added_by=creator_id
        )
        workspace.members[creator_id] = owner
        
        self.workspaces[workspace.workspace_id] = workspace
        self.logger.info(f"Created workspace {workspace.workspace_id}")
        
        return workspace
    
    async def add_member(
        self,
        workspace_id: str,
        user_id: str,
        username: str,
        display_name: str,
        role: Role,
        added_by: str
    ) -> WorkspaceMember:
        """Add a member to workspace"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check if adder has permission
        adder = workspace.members.get(added_by)
        if not adder or not adder.has_permission(Permission.ADMIN):
            raise PermissionError("No permission to add members")
        
        member = WorkspaceMember(
            user_id=user_id,
            username=username,
            display_name=display_name,
            role=role,
            added_by=added_by
        )
        
        workspace.members[user_id] = member
        
        # Broadcast update
        await self._broadcast_update(workspace_id, "member_added", {
            "user_id": user_id,
            "display_name": display_name,
            "role": role.value
        })
        
        return member
    
    async def update_member_role(
        self,
        workspace_id: str,
        target_user_id: str,
        new_role: Role,
        changed_by: str
    ) -> bool:
        """Update a member's role"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Check permissions
        changer = workspace.members.get(changed_by)
        if not changer or not changer.has_permission(Permission.ADMIN):
            raise PermissionError("No permission to change roles")
        
        target = workspace.members.get(target_user_id)
        if not target:
            return False
        
        # Can't change owner role unless you're owner
        if target.role == Role.OWNER and changer.role != Role.OWNER:
            raise PermissionError("Only owners can modify owner roles")
        
        old_role = target.role
        target.role = new_role
        
        # Broadcast update
        await self._broadcast_update(workspace_id, "role_changed", {
            "user_id": target_user_id,
            "old_role": old_role.value,
            "new_role": new_role.value
        })
        
        return True
    
    async def remove_member(
        self,
        workspace_id: str,
        target_user_id: str,
        removed_by: str
    ) -> bool:
        """Remove a member from workspace"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        remover = workspace.members.get(removed_by)
        if not remover or not remover.has_permission(Permission.ADMIN):
            raise PermissionError("No permission to remove members")
        
        target = workspace.members.get(target_user_id)
        if not target:
            return False
        
        # Can't remove owner
        if target.role == Role.OWNER:
            raise PermissionError("Cannot remove workspace owner")
        
        del workspace.members[target_user_id]
        
        await self._broadcast_update(workspace_id, "member_removed", {
            "user_id": target_user_id
        })
        
        return True
    
    async def _broadcast_update(
        self,
        workspace_id: str,
        update_type: str,
        data: Dict[str, Any]
    ):
        """Broadcast update to all workspace members"""
        update = RealTimeUpdate(
            update_id=secrets.token_urlsafe(16),
            workspace_id=workspace_id,
            update_type=update_type,
            data=data
        )
        await self.update_queue.put(update)


class CommentService:
    """
    Real-time commenting service for positions and strategies.
    """
    
    def __init__(self, config: Dict[str, Any], workspace_manager: WorkspaceManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.workspace_manager = workspace_manager
        self.comments: Dict[str, List[Comment]] = {}  # target_id -> comments
        self.mention_handlers: Dict[str, Callable] = {}
    
    async def add_comment(
        self,
        workspace_id: str,
        author_id: str,
        target_type: str,
        target_id: str,
        content: str,
        comment_type: CommentType = CommentType.GENERAL,
        parent_comment_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None
    ) -> Comment:
        """Add a comment to a target (position, strategy, decision)"""
        workspace = self.workspace_manager.workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
        
        member = workspace.members.get(author_id)
        if not member or not member.has_permission(Permission.COMMENT):
            raise PermissionError("No permission to comment")
        
        # Parse mentions
        mentions = self._extract_mentions(content)
        
        comment = Comment(
            comment_id=secrets.token_urlsafe(16),
            workspace_id=workspace_id,
            author_id=author_id,
            author_name=member.display_name,
            comment_type=comment_type,
            content=content,
            target_type=target_type,
            target_id=target_id,
            parent_comment_id=parent_comment_id,
            attachments=attachments or [],
            mentions=mentions
        )
        
        # Store comment
        if target_id not in self.comments:
            self.comments[target_id] = []
        self.comments[target_id].append(comment)
        
        # Notify mentioned users
        await self._notify_mentions(workspace_id, comment, mentions)
        
        # Broadcast to workspace
        await self.workspace_manager._broadcast_update(workspace_id, "comment_added", {
            "comment_id": comment.comment_id,
            "target_type": target_type,
            "target_id": target_id,
            "author": member.display_name,
            "content": content[:100],
            "comment_type": comment_type.value
        })
        
        return comment
    
    async def get_comments(
        self,
        target_id: str,
        workspace_id: str,
        requester_id: str
    ) -> List[Comment]:
        """Get all comments for a target"""
        workspace = self.workspace_manager.workspaces.get(workspace_id)
        if not workspace:
            return []
        
        if requester_id not in workspace.members:
            return []
        
        comments = self.comments.get(target_id, [])
        return [c for c in comments if not c.is_deleted]
    
    async def add_reaction(
        self,
        comment_id: str,
        user_id: str,
        emoji: str
    ) -> bool:
        """Add a reaction to a comment"""
        for comments in self.comments.values():
            for comment in comments:
                if comment.comment_id == comment_id:
                    if emoji not in comment.reactions:
                        comment.reactions[emoji] = []
                    if user_id not in comment.reactions[emoji]:
                        comment.reactions[emoji].append(user_id)
                    return True
        return False
    
    async def edit_comment(
        self,
        comment_id: str,
        new_content: str,
        editor_id: str
    ) -> bool:
        """Edit a comment (author only)"""
        for comments in self.comments.values():
            for comment in comments:
                if comment.comment_id == comment_id:
                    if comment.author_id != editor_id:
                        raise PermissionError("Only author can edit comment")
                    comment.content = new_content
                    comment.edited_at = datetime.now()
                    return True
        return False
    
    async def delete_comment(
        self,
        comment_id: str,
        deleter_id: str
    ) -> bool:
        """Delete a comment (soft delete)"""
        for target_id, comments in self.comments.items():
            for comment in comments:
                if comment.comment_id == comment_id:
                    workspace = self.workspace_manager.workspaces.get(comment.workspace_id)
                    if not workspace:
                        return False
                    
                    member = workspace.members.get(deleter_id)
                    if comment.author_id != deleter_id and not member.has_permission(Permission.ADMIN):
                        raise PermissionError("No permission to delete comment")
                    
                    comment.is_deleted = True
                    return True
        return False
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from content"""
        import re
        mentions = re.findall(r'@(\w+)', content)
        return mentions
    
    async def _notify_mentions(
        self,
        workspace_id: str,
        comment: Comment,
        mentions: List[str]
    ):
        """Notify mentioned users"""
        workspace = self.workspace_manager.workspaces.get(workspace_id)
        if not workspace:
            return
        
        for mention in mentions:
            # Find user by username
            for user_id, member in workspace.members.items():
                if member.username == mention:
                    # Send notification
                    await self.workspace_manager._broadcast_update(
                        workspace_id,
                        "mention_notification",
                        {
                            "recipient_id": user_id,
                            "comment_id": comment.comment_id,
                            "author": comment.author_name,
                            "content": comment.content[:100]
                        }
                    )


class VotingSystem:
    """
    Decision voting system for group investment choices.
    """
    
    def __init__(self, config: Dict[str, Any], workspace_manager: WorkspaceManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.workspace_manager = workspace_manager
        self.decisions: Dict[str, Decision] = {}
    
    async def create_decision(
        self,
        workspace_id: str,
        title: str,
        description: str,
        decision_type: str,
        creator_id: str,
        proposed_actions: List[Dict[str, Any]],
        expected_impact: Optional[Dict[str, Any]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """Create a new decision for voting"""
        workspace = self.workspace_manager.workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
        
        member = workspace.members.get(creator_id)
        if not member or not member.has_permission(Permission.EDIT):
            raise PermissionError("No permission to create decisions")
        
        # Calculate voting deadline
        voting_hours = workspace.voting_config.get("voting_period_hours", 24)
        
        # Determine required approvers
        required_approvers = []
        if workspace.voting_config.get("require_risk_approval"):
            for uid, m in workspace.members.items():
                if m.role == Role.RISK_OFFICER:
                    required_approvers.append(uid)
        if workspace.voting_config.get("require_compliance_approval"):
            for uid, m in workspace.members.items():
                if m.role == Role.COMPLIANCE_OFFICER:
                    required_approvers.append(uid)
        
        decision = Decision(
            decision_id=secrets.token_urlsafe(16),
            workspace_id=workspace_id,
            title=title,
            description=description,
            decision_type=decision_type,
            created_by=creator_id,
            status=DecisionStatus.PENDING_VOTES,
            voting_deadline=datetime.now() + timedelta(hours=voting_hours),
            required_approvers=required_approvers,
            min_approval_percentage=workspace.voting_config.get("approval_threshold", 0.6),
            proposed_actions=proposed_actions,
            expected_impact=expected_impact or {},
            risk_assessment=risk_assessment or {}
        )
        
        self.decisions[decision.decision_id] = decision
        
        # Broadcast to workspace
        await self.workspace_manager._broadcast_update(workspace_id, "decision_created", {
            "decision_id": decision.decision_id,
            "title": title,
            "decision_type": decision_type,
            "creator": member.display_name,
            "voting_deadline": decision.voting_deadline.isoformat()
        })
        
        return decision
    
    async def cast_vote(
        self,
        decision_id: str,
        voter_id: str,
        vote_type: VoteType,
        comment: str = "",
        conditions: Optional[List[str]] = None
    ) -> Vote:
        """Cast a vote on a decision"""
        decision = self.decisions.get(decision_id)
        if not decision:
            raise ValueError("Decision not found")
        
        if decision.status != DecisionStatus.PENDING_VOTES:
            raise ValueError(f"Decision is not open for voting (status: {decision.status.value})")
        
        if decision.voting_deadline and datetime.now() > decision.voting_deadline:
            decision.status = DecisionStatus.EXPIRED
            raise ValueError("Voting period has ended")
        
        workspace = self.workspace_manager.workspaces.get(decision.workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
        
        member = workspace.members.get(voter_id)
        if not member:
            raise PermissionError("Not a workspace member")
        
        # Check if can vote (need APPROVE permission for approve/reject)
        if vote_type in [VoteType.APPROVE, VoteType.REJECT, VoteType.CONDITIONAL]:
            if not member.has_permission(Permission.APPROVE) and not member.has_permission(Permission.EDIT):
                raise PermissionError("No permission to vote on decisions")
        
        # Calculate vote weight based on role
        weight = self._calculate_vote_weight(member.role)
        
        vote = Vote(
            vote_id=secrets.token_urlsafe(16),
            decision_id=decision_id,
            voter_id=voter_id,
            voter_name=member.display_name,
            voter_role=member.role,
            vote_type=vote_type,
            comment=comment,
            conditions=conditions or [],
            weight=weight
        )
        
        decision.votes[voter_id] = vote
        
        # Check if decision can be resolved
        await self._check_decision_resolution(decision)
        
        # Broadcast vote
        await self.workspace_manager._broadcast_update(decision.workspace_id, "vote_cast", {
            "decision_id": decision_id,
            "voter": member.display_name,
            "vote_type": vote_type.value,
            "current_approval": decision.calculate_approval_percentage()
        })
        
        return vote
    
    async def _check_decision_resolution(self, decision: Decision):
        """Check if decision can be resolved based on votes"""
        workspace = self.workspace_manager.workspaces.get(decision.workspace_id)
        if not workspace:
            return
        
        min_votes = workspace.voting_config.get("min_votes_required", 2)
        
        # Check required approvers
        for required_id in decision.required_approvers:
            if required_id not in decision.votes:
                return  # Still waiting for required approver
            if decision.votes[required_id].vote_type == VoteType.REJECT:
                decision.status = DecisionStatus.REJECTED
                decision.final_result = "Rejected by required approver"
                return
        
        # Check if we have enough votes
        if len(decision.votes) < min_votes:
            return
        
        # Calculate approval
        approval_pct = decision.calculate_approval_percentage()
        
        if approval_pct >= decision.min_approval_percentage:
            decision.status = DecisionStatus.APPROVED
            decision.final_result = f"Approved with {approval_pct*100:.1f}% approval"
        elif len(decision.votes) >= len(workspace.members) * 0.75:
            # Most members have voted and threshold not met
            decision.status = DecisionStatus.REJECTED
            decision.final_result = f"Rejected with {approval_pct*100:.1f}% approval"
    
    async def execute_decision(
        self,
        decision_id: str,
        executor_id: str,
        execution_details: Dict[str, Any]
    ) -> bool:
        """Execute an approved decision"""
        decision = self.decisions.get(decision_id)
        if not decision:
            return False
        
        if decision.status != DecisionStatus.APPROVED:
            raise ValueError("Decision is not approved")
        
        workspace = self.workspace_manager.workspaces.get(decision.workspace_id)
        if not workspace:
            return False
        
        member = workspace.members.get(executor_id)
        if not member or not member.has_permission(Permission.TRADE):
            raise PermissionError("No permission to execute decisions")
        
        decision.status = DecisionStatus.EXECUTED
        decision.executed_at = datetime.now()
        decision.execution_details = execution_details
        
        # Broadcast execution
        await self.workspace_manager._broadcast_update(decision.workspace_id, "decision_executed", {
            "decision_id": decision_id,
            "executor": member.display_name,
            "execution_time": decision.executed_at.isoformat()
        })
        
        return True
    
    async def get_pending_decisions(self, workspace_id: str) -> List[Decision]:
        """Get all pending decisions for a workspace"""
        return [
            d for d in self.decisions.values()
            if d.workspace_id == workspace_id and d.status == DecisionStatus.PENDING_VOTES
        ]
    
    def _calculate_vote_weight(self, role: Role) -> float:
        """Calculate vote weight based on role"""
        weights = {
            Role.VIEWER: 0.0,
            Role.ANALYST: 0.5,
            Role.TRADER: 0.8,
            Role.PORTFOLIO_MANAGER: 1.5,
            Role.RISK_OFFICER: 1.2,
            Role.COMPLIANCE_OFFICER: 1.0,
            Role.ADMIN: 1.0,
            Role.OWNER: 2.0
        }
        return weights.get(role, 1.0)


class AuditTrailService:
    """
    Complete audit trail for all collaborative decisions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.audit_logs: Dict[str, List[AuditLogEntry]] = {}  # workspace_id -> entries
    
    async def log_action(
        self,
        workspace_id: str,
        action: AuditAction,
        actor_id: str,
        actor_name: str,
        target_type: str = "",
        target_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = ""
    ) -> AuditLogEntry:
        """Log an auditable action"""
        entry = AuditLogEntry(
            entry_id=secrets.token_urlsafe(16),
            workspace_id=workspace_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            previous_state=previous_state,
            new_state=new_state,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if workspace_id not in self.audit_logs:
            self.audit_logs[workspace_id] = []
        
        self.audit_logs[workspace_id].append(entry)
        
        # Also log to main logger for centralized logging
        self.logger.info(
            f"AUDIT: {action.value} by {actor_name} in workspace {workspace_id[:8]} - "
            f"target: {target_type}/{target_id}"
        )
        
        return entry
    
    async def get_audit_log(
        self,
        workspace_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLogEntry]:
        """Get audit log entries with optional filters"""
        entries = self.audit_logs.get(workspace_id, [])
        
        if filters:
            if "action" in filters:
                entries = [e for e in entries if e.action.value == filters["action"]]
            if "actor_id" in filters:
                entries = [e for e in entries if e.actor_id == filters["actor_id"]]
            if "target_type" in filters:
                entries = [e for e in entries if e.target_type == filters["target_type"]]
            if "start_date" in filters:
                start = datetime.fromisoformat(filters["start_date"])
                entries = [e for e in entries if e.timestamp >= start]
            if "end_date" in filters:
                end = datetime.fromisoformat(filters["end_date"])
                entries = [e for e in entries if e.timestamp <= end]
        
        # Sort by timestamp descending
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries[offset:offset + limit]
    
    async def export_audit_log(
        self,
        workspace_id: str,
        format: str = "json"
    ) -> str:
        """Export audit log for compliance reporting"""
        entries = self.audit_logs.get(workspace_id, [])
        
        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2, default=str)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "timestamp", "action", "actor_name", "target_type", "target_id", "details"
            ])
            writer.writeheader()
            
            for entry in entries:
                writer.writerow({
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action.value,
                    "actor_name": entry.actor_name,
                    "target_type": entry.target_type,
                    "target_id": entry.target_id,
                    "details": json.dumps(entry.details)
                })
            
            return output.getvalue()
        
        return ""


class CollaborationPlatform:
    """
    Main collaboration platform integrating all features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.workspace_manager = WorkspaceManager(config)
        self.comment_service = CommentService(config, self.workspace_manager)
        self.voting_system = VotingSystem(config, self.workspace_manager)
        self.audit_service = AuditTrailService(config)
    
    async def initialize(self):
        """Initialize collaboration platform"""
        self.logger.info("Initializing Collaboration Platform...")
        # Start update broadcaster
        asyncio.create_task(self._update_broadcaster())
    
    async def _update_broadcaster(self):
        """Broadcast real-time updates to connected clients"""
        while True:
            try:
                update = await self.workspace_manager.update_queue.get()
                # In production, send to WebSocket connections
                self.logger.debug(f"Broadcasting update: {update.update_type}")
            except Exception as e:
                self.logger.error(f"Update broadcaster error: {e}")
            await asyncio.sleep(0.1)
    
    def get_api_routes(self):
        """Get FastAPI routes for collaboration endpoints"""
        from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
        from pydantic import BaseModel
        
        router = APIRouter(prefix="/collaboration", tags=["Collaboration"])
        
        class CreateWorkspaceRequest(BaseModel):
            name: str
            description: str
            settings: Optional[Dict[str, Any]] = None
        
        class AddMemberRequest(BaseModel):
            user_id: str
            username: str
            display_name: str
            role: str
        
        class CreateDecisionRequest(BaseModel):
            title: str
            description: str
            decision_type: str
            proposed_actions: List[Dict[str, Any]]
            expected_impact: Optional[Dict[str, Any]] = None
        
        class CastVoteRequest(BaseModel):
            vote_type: str
            comment: str = ""
            conditions: List[str] = []
        
        class AddCommentRequest(BaseModel):
            target_type: str
            target_id: str
            content: str
            comment_type: str = "general"
            parent_comment_id: Optional[str] = None
        
        @router.post("/workspaces")
        async def create_workspace(request: CreateWorkspaceRequest, user_id: str = "demo_user"):
            workspace = await self.workspace_manager.create_workspace(
                name=request.name,
                description=request.description,
                creator_id=user_id,
                creator_name="Demo User",
                settings=request.settings
            )
            
            await self.audit_service.log_action(
                workspace_id=workspace.workspace_id,
                action=AuditAction.WORKSPACE_CREATED,
                actor_id=user_id,
                actor_name="Demo User",
                details={"name": request.name}
            )
            
            return {
                "workspace_id": workspace.workspace_id,
                "name": workspace.name,
                "created_at": workspace.created_at.isoformat()
            }
        
        @router.get("/workspaces/{workspace_id}")
        async def get_workspace(workspace_id: str, user_id: str = "demo_user"):
            workspace = self.workspace_manager.workspaces.get(workspace_id)
            if not workspace:
                raise HTTPException(status_code=404, detail="Workspace not found")
            
            if user_id not in workspace.members:
                raise HTTPException(status_code=403, detail="Access denied")
            
            return {
                "workspace_id": workspace.workspace_id,
                "name": workspace.name,
                "description": workspace.description,
                "members": [
                    {
                        "user_id": m.user_id,
                        "display_name": m.display_name,
                        "role": m.role.value
                    }
                    for m in workspace.members.values()
                ],
                "voting_config": workspace.voting_config
            }
        
        @router.post("/workspaces/{workspace_id}/members")
        async def add_member(workspace_id: str, request: AddMemberRequest, user_id: str = "demo_user"):
            member = await self.workspace_manager.add_member(
                workspace_id=workspace_id,
                user_id=request.user_id,
                username=request.username,
                display_name=request.display_name,
                role=Role(request.role),
                added_by=user_id
            )
            
            await self.audit_service.log_action(
                workspace_id=workspace_id,
                action=AuditAction.MEMBER_ADDED,
                actor_id=user_id,
                actor_name="Demo User",
                target_type="member",
                target_id=request.user_id,
                details={"role": request.role}
            )
            
            return {"status": "added", "user_id": member.user_id}
        
        @router.post("/workspaces/{workspace_id}/decisions")
        async def create_decision(workspace_id: str, request: CreateDecisionRequest, user_id: str = "demo_user"):
            decision = await self.voting_system.create_decision(
                workspace_id=workspace_id,
                title=request.title,
                description=request.description,
                decision_type=request.decision_type,
                creator_id=user_id,
                proposed_actions=request.proposed_actions,
                expected_impact=request.expected_impact
            )
            
            await self.audit_service.log_action(
                workspace_id=workspace_id,
                action=AuditAction.DECISION_CREATED,
                actor_id=user_id,
                actor_name="Demo User",
                target_type="decision",
                target_id=decision.decision_id,
                details={"title": request.title, "type": request.decision_type}
            )
            
            return {
                "decision_id": decision.decision_id,
                "status": decision.status.value,
                "voting_deadline": decision.voting_deadline.isoformat()
            }
        
        @router.post("/decisions/{decision_id}/vote")
        async def cast_vote(decision_id: str, request: CastVoteRequest, user_id: str = "demo_user"):
            vote = await self.voting_system.cast_vote(
                decision_id=decision_id,
                voter_id=user_id,
                vote_type=VoteType(request.vote_type),
                comment=request.comment,
                conditions=request.conditions
            )
            
            decision = self.voting_system.decisions.get(decision_id)
            
            await self.audit_service.log_action(
                workspace_id=decision.workspace_id,
                action=AuditAction.VOTE_CAST,
                actor_id=user_id,
                actor_name="Demo User",
                target_type="decision",
                target_id=decision_id,
                details={"vote_type": request.vote_type}
            )
            
            return {
                "vote_id": vote.vote_id,
                "decision_status": decision.status.value,
                "approval_percentage": decision.calculate_approval_percentage()
            }
        
        @router.get("/decisions/{decision_id}")
        async def get_decision(decision_id: str):
            decision = self.voting_system.decisions.get(decision_id)
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")
            
            return {
                "decision_id": decision.decision_id,
                "title": decision.title,
                "description": decision.description,
                "status": decision.status.value,
                "votes": [
                    {
                        "voter_name": v.voter_name,
                        "vote_type": v.vote_type.value,
                        "comment": v.comment
                    }
                    for v in decision.votes.values()
                ],
                "approval_percentage": decision.calculate_approval_percentage(),
                "voting_deadline": decision.voting_deadline.isoformat() if decision.voting_deadline else None
            }
        
        @router.post("/workspaces/{workspace_id}/comments")
        async def add_comment(workspace_id: str, request: AddCommentRequest, user_id: str = "demo_user"):
            comment = await self.comment_service.add_comment(
                workspace_id=workspace_id,
                author_id=user_id,
                target_type=request.target_type,
                target_id=request.target_id,
                content=request.content,
                comment_type=CommentType(request.comment_type),
                parent_comment_id=request.parent_comment_id
            )
            
            await self.audit_service.log_action(
                workspace_id=workspace_id,
                action=AuditAction.COMMENT_ADDED,
                actor_id=user_id,
                actor_name="Demo User",
                target_type=request.target_type,
                target_id=request.target_id,
                details={"comment_id": comment.comment_id}
            )
            
            return {
                "comment_id": comment.comment_id,
                "created_at": comment.created_at.isoformat()
            }
        
        @router.get("/comments/{target_id}")
        async def get_comments(target_id: str, workspace_id: str, user_id: str = "demo_user"):
            comments = await self.comment_service.get_comments(target_id, workspace_id, user_id)
            return {
                "comments": [
                    {
                        "comment_id": c.comment_id,
                        "author_name": c.author_name,
                        "content": c.content,
                        "comment_type": c.comment_type.value,
                        "created_at": c.created_at.isoformat(),
                        "reactions": c.reactions
                    }
                    for c in comments
                ]
            }
        
        @router.get("/workspaces/{workspace_id}/audit-log")
        async def get_audit_log(
            workspace_id: str,
            limit: int = 100,
            offset: int = 0,
            user_id: str = "demo_user"
        ):
            entries = await self.audit_service.get_audit_log(
                workspace_id=workspace_id,
                limit=limit,
                offset=offset
            )
            return {
                "entries": [e.to_dict() for e in entries],
                "total": len(self.audit_service.audit_logs.get(workspace_id, []))
            }
        
        @router.websocket("/ws/{workspace_id}")
        async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
            await websocket.accept()
            
            if workspace_id not in self.workspace_manager.websocket_connections:
                self.workspace_manager.websocket_connections[workspace_id] = set()
            
            self.workspace_manager.websocket_connections[workspace_id].add(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    # Handle incoming WebSocket messages
            except WebSocketDisconnect:
                self.workspace_manager.websocket_connections[workspace_id].discard(websocket)
        
        return router


# Export main components
__all__ = [
    'CollaborationPlatform',
    'WorkspaceManager',
    'CommentService',
    'VotingSystem',
    'AuditTrailService',
    'Permission',
    'Role',
    'VoteType',
    'DecisionStatus',
    'AuditAction'
]
