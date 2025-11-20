# Complete Permission Guide - AgriAssist Chatbot

## Overview

Every permission follows this pattern:
```
Can [ACTION] [MODEL]
```

**Actions:**
- **Add** = Create new records
- **View** = Read/view records
- **Change** = Edit existing records
- **Delete** = Remove records

---

## Permissions You Actually Need (For Your App)

### 1. CHATBOT PERMISSIONS (Main App)

#### Agricultural FAQ Management
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view agricultural faq` | Read all FAQs | Farmers, Officers |
| `Can add agricultural faq` | Create new FAQs | Officers, Admins |
| `Can change agricultural faq` | Edit existing FAQs | Officers, Admins |
| `Can delete agricultural faq` | Remove FAQs | Admins only |

**Example Use Case:**
- Give Officers: View + Add + Change (can create and edit FAQs)
- Give Farmers: View only (can read but not edit)

---

#### Chat Session Management
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view chat session` | See chat conversations | Officers, Admins |
| `Can add chat session` | Start a new chat | Everyone (handled by code) |
| `Can change chat session` | Modify chat metadata | Admins |
| `Can delete chat session` | Remove chat sessions | Admins |

**Example Use Case:**
- Give Officers: View + Delete (monitor and clean up chats)
- Regular users don't need these (handled automatically)

---

#### Chat Messages
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view chat message` | Read messages in chats | Officers, Admins |
| `Can add chat message` | Send a message | Everyone (handled by code) |
| `Can change chat message` | Edit a message | Admins only |
| `Can delete chat message` | Remove a message | Admins |

**Example Use Case:**
- Give Officers: View (see all chat messages)
- Regular code handles message sending automatically

---

#### Pest Information
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view pest info` | Read pest database | Everyone |
| `Can add pest info` | Add new pest | Officers, Admins |
| `Can change pest info` | Update pest info | Officers, Admins |
| `Can delete pest info` | Remove pest entry | Admins |

**Example Use Case:**
- Give Officers: View + Add + Change (manage pest database)
- Give Farmers: View only

---

#### Fertilizer Guidelines
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view fertilizer guideline` | Read fertilizer info | Everyone |
| `Can add fertilizer guideline` | Create new guideline | Officers, Admins |
| `Can change fertilizer guideline` | Edit guideline | Officers, Admins |
| `Can delete fertilizer guideline` | Remove guideline | Admins |

**Example Use Case:**
- Give Officers: View + Add + Change
- Give Farmers: View only

---

#### Crop Management Tips
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view crop management tip` | Read farming tips | Everyone |
| `Can add crop management tip` | Create new tip | Officers, Admins |
| `Can change crop management tip` | Edit tip | Officers, Admins |
| `Can delete crop management tip` | Remove tip | Admins |

**Example Use Case:**
- Give Officers: Full access (View, Add, Change)
- Give Farmers: View only

---

#### Extension Resources
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view extension resource` | Read resources | Everyone |
| `Can add extension resource` | Add new resource | Officers, Admins |
| `Can change extension resource` | Edit resource | Officers, Admins |
| `Can delete extension resource` | Remove resource | Admins |

**Example Use Case:**
- Give Officers: View + Add + Change
- Give Farmers: View only

---

#### User Profiles
| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view user profile` | See user profiles | Officers, Admins |
| `Can add user profile` | Create profile | Admins |
| `Can change user profile` | Edit profile | Admins |
| `Can delete user profile` | Remove profile | Admins |

**Example Use Case:**
- Give Officers: View only (see who's using the app)
- Regular users: Auto-created, no permission needed

---

### 2. AUTH PERMISSIONS (User Management - Don't give to regular users!)

| Permission | What It Does | Useful For |
|-----------|-------------|-----------|
| `Can view user` | See all users | Admins |
| `Can add user` | Create new user account | Admins |
| `Can change user` | Edit user account | Admins |
| `Can delete user` | Remove user account | Admins |
| `Can view group` | See groups | Admins |
| `Can add group` | Create group | Admins |
| `Can change group` | Edit group | Admins |
| `Can delete group` | Remove group | Admins |

⚠️ **WARNING:** Don't give these to regular officers! They'll be able to create/delete users.

---

### 3. SYSTEM PERMISSIONS (Ignore these - Backend only)

| Permission | Purpose |
|-----------|---------|
| `Can add/view/change/delete log entry` | System logging (ignore) |
| `Can add/view/change/delete permission` | System permissions (ignore) |
| `Can add/view/change/delete content type` | System Django stuff (ignore) |
| `Can add/view/change/delete session` | User sessions (ignore) |

⚠️ **Don't assign these to anyone.**

---

## Real-World Permission Scenarios

### Scenario 1: Farmer User
**Goal:** Can chat but can't manage content

**Permissions to give:**
- ✓ `Can view agricultural faq`
- ✓ `Can view pest info`
- ✓ `Can view fertilizer guideline`
- ✓ `Can view crop management tip`
- ✓ `Can view extension resource`

**Steps:**
1. Admin panel → Users → farmer1
2. Check "Staff status" (so they can access admin panel)
3. Permissions section → Select the 5 "view" permissions above
4. Click Save

**Result:** Farmer can view FAQs, tips, etc. but can't edit or create

---

### Scenario 2: Extension Officer
**Goal:** Can manage all agricultural content

**Permissions to give:**
- ✓ `Can view agricultural faq`
- ✓ `Can add agricultural faq`
- ✓ `Can change agricultural faq`
- ✓ `Can delete agricultural faq`
- ✓ `Can view pest info`
- ✓ `Can add pest info`
- ✓ `Can change pest info`
- ✓ `Can delete pest info`
- ✓ `Can view fertilizer guideline`
- ✓ `Can add fertilizer guideline`
- ✓ `Can change fertilizer guideline`
- ✓ `Can delete fertilizer guideline`
- ✓ `Can view crop management tip`
- ✓ `Can add crop management tip`
- ✓ `Can change crop management tip`
- ✓ `Can delete crop management tip`
- ✓ `Can view extension resource`
- ✓ `Can add extension resource`
- ✓ `Can change extension resource`
- ✓ `Can delete extension resource`
- ✓ `Can view chat session`
- ✓ `Can delete chat session`
- ✓ `Can view chat message`

**Steps:**
1. Admin panel → Users → officer1
2. Check "Staff status"
3. Permissions section → Select all permissions above
4. Click Save

**Result:** Officer has full control over content and can monitor chats

---

### Scenario 3: Admin User
**Goal:** Full system access

**Permissions to give:**
- Everything (or just check "Superuser" status and they get all permissions automatically)

**Steps:**
1. Admin panel → Users → admin1
2. Check "Staff status"
3. Check "Superuser status"
4. Click Save

**Result:** Admin has complete access to everything

---

## How Permissions Work in Code

### When User Tries to Access Something:

1. **User accesses admin panel**
   ```
   Has "Staff status" checked?
   → Yes: Can see admin panel
   → No: Access denied
   ```

2. **User views Agricultural FAQs**
   ```
   Has permission "Can view agricultural faq"?
   → Yes: Shows list of FAQs
   → No: FDA option hidden in sidebar
   ```

3. **User tries to edit an FAQ**
   ```
   Has permission "Can change agricultural faq"?
   → Yes: Shows edit form, can save
   → No: Edit button disabled, changes not saved
   ```

4. **User tries to delete an FAQ**
   ```
   Has permission "Can delete agricultural faq"?
   → Yes: Delete button works, deletes record
   → No: Delete button hidden/disabled
   ```

---

## Quick Reference Table

| User Type | Should Have Staff Status? | Key Permissions |
|-----------|--------------------------|-----------------|
| Farmer | ❌ No | view_agriculturalFaq, view_pestinfo, etc. |
| Officer | ✅ Yes | All "view", "add", "change" permissions |
| Admin | ✅ Yes + Superuser | All permissions |

---

## Common Permission Mistakes

❌ **Mistake 1:** Giving user permissions without checking "Staff status"
- **Fix:** Always check Staff status first!

❌ **Mistake 2:** Giving "User management" permissions to officers
- **Fix:** Only give Officers content management permissions, not user permissions

❌ **Mistake 3:** Giving "Delete" permissions to everyone
- **Fix:** Only admins should delete

❌ **Mistake 4:** Assigning random permissions
- **Fix:** Follow the scenarios above

---

## Permission Checking in Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

user = User.objects.get(username='officer1')

# Check specific permission
if user.has_perm('chatbot.view_agriculturalFaq'):
    print("✓ Can view FAQs")

# Check multiple permissions
perms = [
    'chatbot.view_agriculturalFaq',
    'chatbot.add_agriculturalFaq',
    'chatbot.change_agriculturalFaq',
]

for perm in perms:
    status = "✓" if user.has_perm(perm) else "✗"
    print(f"{status} {perm}")

# Get all permissions
print("\nAll permissions for officer1:")
for perm in user.get_all_permissions():
    print(f"  - {perm}")

exit()
```

---

## Summary

**Three types of permissions:**

1. **Content Permissions** (Agricultural data)
   - View, Add, Change, Delete FAQs, Pests, Fertilizers, Tips, Resources

2. **User Permissions** (Admin only)
   - Manage users and groups

3. **System Permissions** (Ignore)
   - Backend logging, sessions, etc.

**Best Practice:**
- Give Farmers: View-only permissions
- Give Officers: View + Add + Change + Delete for content
- Give Admins: Everything

---

**Need to set up permissions for a specific role?** Let me know the role name and what they should be able to do, and I'll give you the exact list! 👍
