# Azure AD Permissions Status

## ✅ Current Permissions (All Granted)

Your Azure AD app registration has **all required permissions** for widget exports:

### Configured Permissions (8)
1. ✅ **Files.ReadWrite** (Delegated) - Have full access to user files
2. ✅ **Mail.ReadWrite** (Delegated) - Read and write access to user mail
3. ✅ **Mail.ReadWrite** (Application) - Read and write mail in all mailboxes
4. ✅ **Mail.ReadWrite.Shared** (Delegated) - Read and write user and shared mail
5. ✅ **Mail.Send** (Delegated) - Send mail as a user ⭐ **Required for email exports**
6. ✅ **Mail.Send** (Application) - Send mail as any user
7. ✅ **offline_access** (Delegated) - Maintain access to data ⭐ **Required for refresh tokens**
8. ✅ **User.Read** (Delegated) - Sign in and read user profile

### Other Permissions Granted (4)
1. ✅ **Files.ReadWrite.All** (Delegated) - Have full access to all files ⭐ **Required for OneDrive uploads**
2. ✅ **Mail.Read** (Delegated) - Read user mail
3. ✅ **openid** (Delegated) - Sign users in
4. ✅ **profile** (Delegated) - View users' basic profile

## 📋 Required SCOPE Environment Variable

Update your `SCOPE` environment variable in Render to include all granted permissions:

```bash
SCOPE=https://graph.microsoft.com/User.Read https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/Files.ReadWrite.All https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/offline_access
```

✅ **Calendars.ReadWrite has been added to Azure AD!**

## ✅ What You Can Do Now

With these permissions, you can:

1. **Send Emails via Outlook** ✅
   - Use `Mail.Send` permission
   - Send widget exports as email attachments

2. **Upload to OneDrive** ✅
   - Use `Files.ReadWrite` or `Files.ReadWrite.All`
   - Upload PDF, Word, Excel, PowerPoint files

3. **User Authentication** ✅
   - Use `User.Read` permission
   - Get user profile information

4. **Token Refresh** ✅
   - Use `offline_access` permission
   - Automatically refresh expired tokens

## 🔄 Next Steps

1. **Update SCOPE in Render**: Add the SCOPE environment variable with all permissions
2. **Re-authenticate Users**: Users may need to re-authenticate to get tokens with new scopes
3. **Test Export Features**: Test email and OneDrive upload functionality

## 📝 Permission Summary

| Permission | Type | Status | Use Case |
|------------|------|--------|----------|
| User.Read | Delegated | ✅ Granted | User authentication |
| Mail.Send | Delegated | ✅ Granted | Send emails via Outlook |
| Files.ReadWrite | Delegated | ✅ Granted | Upload to OneDrive |
| Files.ReadWrite.All | Delegated | ✅ Granted | Full OneDrive access |
| offline_access | Delegated | ✅ Granted | Token refresh |
| Calendars.ReadWrite | Delegated | ✅ Granted | Calendar integration |

**All widget export permissions are ready!** 🎉

