from backend.core.common import BaseRepository


class UserRepository(BaseRepository):

    async def get_all(self):
        return [
            {
                'name': 'vadim',
            },
            {
                'name': 'dmitry',
            }
        ]

#     A
#    /
#    B
#   C  D
#
# id || user || text || parent_id
# 1              A         None
# 2              B           1
# 3              C           2
# 4              D           2
#
#
#
#
# porst_id   User  text
