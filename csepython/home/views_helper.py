# ============ HELPER FUNCTIONS ============
def is_manager(user):
    try:
        return user.profile.role == "manager"
    except:
        return False

def is_sales_agent(user):
    try:
        return user.profile.role == "salesagent"
    except:
        return False
