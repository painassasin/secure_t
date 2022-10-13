from alembic import op


revision = 'd86c75053019'
down_revision = '522b4a596df8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name='ck_parent_id_does_not_refer_itself',
        table_name='posts',
        condition='id <> parent_id'
    )


def downgrade() -> None:
    op.drop_constraint(constraint_name='ck_parent_id_does_not_refer_itself', table_name='posts')
