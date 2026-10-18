"""Add regions routing briefs reviews

Revision ID: a2c3d4e5f678
Revises: f1b8a92e4501
Create Date: 2026-10-18 01:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a2c3d4e5f678'
down_revision: Union[str, Sequence[str], None] = 'f1b8a92e4501'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add region to stores
    with op.batch_alter_table('stores') as batch_op:
        batch_op.add_column(sa.Column('region', sa.String(length=50), nullable=True))
        batch_op.create_index('ix_stores_region', ['region'], unique=False)

    # 2. Add routing and actionability to incidents
    with op.batch_alter_table('incidents') as batch_op:
        batch_op.add_column(sa.Column('primary_owner', sa.String(length=50), nullable=False, server_default='Store Ops'))
        batch_op.add_column(sa.Column('secondary_owner', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('needs_human_review', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('routing_history', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('actionability_score', sa.Float(), nullable=False, server_default='0.85'))
        batch_op.create_index('ix_incidents_primary_owner', ['primary_owner'], unique=False)
        batch_op.create_index('ix_incidents_needs_human_review', ['needs_human_review'], unique=False)

    # 3. Add channel, rating, language to feedback_records
    with op.batch_alter_table('feedback_records') as batch_op:
        batch_op.add_column(sa.Column('channel', sa.String(length=50), nullable=False, server_default='Online Reviews'))
        batch_op.add_column(sa.Column('rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('language', sa.String(length=20), nullable=False, server_default='en'))
        batch_op.create_index('ix_feedback_records_channel', ['channel'], unique=False)

    # 4. Create regional_briefs table
    op.create_table(
        'regional_briefs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=False),
        sa.Column('week_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('week_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('executive_summary', sa.Text(), nullable=False),
        sa.Column('top_issues_json', sa.JSON(), nullable=False),
        sa.Column('low_volume_safety_json', sa.JSON(), nullable=True),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_regional_briefs_region', 'regional_briefs', ['region'], unique=False)
    op.create_index('ix_regional_briefs_week_start', 'regional_briefs', ['week_start'], unique=False)

    # 5. Create escalation_reviews table
    op.create_table(
        'escalation_reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('incident_id', sa.String(length=36), nullable=False),
        sa.Column('is_truly_actionable', sa.Boolean(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewer_id', sa.String(length=36), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_escalation_reviews_incident_id', 'escalation_reviews', ['incident_id'], unique=True)
    op.create_index('ix_escalation_reviews_is_truly_actionable', 'escalation_reviews', ['is_truly_actionable'], unique=False)


def downgrade() -> None:
    op.drop_table('escalation_reviews')
    op.drop_table('regional_briefs')
    with op.batch_alter_table('feedback_records') as batch_op:
        batch_op.drop_index('ix_feedback_records_channel')
        batch_op.drop_column('language')
        batch_op.drop_column('rating')
        batch_op.drop_column('channel')
    with op.batch_alter_table('incidents') as batch_op:
        batch_op.drop_index('ix_incidents_needs_human_review')
        batch_op.drop_index('ix_incidents_primary_owner')
        batch_op.drop_column('actionability_score')
        batch_op.drop_column('routing_history')
        batch_op.drop_column('needs_human_review')
        batch_op.drop_column('secondary_owner')
        batch_op.drop_column('primary_owner')
    with op.batch_alter_table('stores') as batch_op:
        batch_op.drop_index('ix_stores_region')
        batch_op.drop_column('region')
