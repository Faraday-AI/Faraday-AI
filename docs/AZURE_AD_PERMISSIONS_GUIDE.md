# Azure AD App Registration - API Permissions Guide

This guide shows you how to add Microsoft Graph API permissions to your Azure AD app registration.

## 📍 Where to Find Your App Registration

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to Azure Active Directory** (or **Microsoft Entra ID**)
3. **Click "App registrations"** in the left menu
4. **Find your app** (search by name or Client ID: `5accd5f0-bba2-4d4d-b638-7b5587525216`)

## 🔐 Adding API Permissions

### Step 1: Navigate to API Permissions

1. In your app registration, click **"API permissions"** in the left menu
2. You'll see a list of existing permissions

### Step 2: Add Microsoft Graph Permissions

1. Click **"+ Add a permission"** button
2. Select **"Microsoft Graph"** tab (should be selected by default)
3. Choose **"Delegated permissions"** (for user context) or **"Application permissions"** (for app-only)

**For widget exports, you need Delegated permissions** (user must be logged in):

#### Required Permissions for Widget Exports:

1. **Mail.Send**
   - **Type**: Delegated
   - **Description**: Send mail as the user
   - **Use case**: Send widget exports via Outlook email

2. **Files.ReadWrite**
   - **Type**: Delegated
   - **Description**: Have full access to user files
   - **Use case**: Upload widget exports to OneDrive

3. **Files.ReadWrite.All** (Optional - if Files.ReadWrite doesn't work)
   - **Type**: Delegated
   - **Description**: Have full access to all files user can access
   - **Use case**: Full OneDrive access

4. **Sites.ReadWrite.All** (Optional - for SharePoint)
   - **Type**: Delegated
   - **Description**: Read and write items in all site collections
   - **Use case**: Upload to SharePoint if needed

### Step 3: Grant Admin Consent

⚠️ **IMPORTANT**: After adding permissions, you must grant admin consent:

1. Click **"Grant admin consent for [Your Organization]"** button
2. Confirm the consent
3. All permissions should show **"Granted for [Your Organization]"** with a green checkmark

### Step 4: Verify Permissions

Your API permissions list should show:

```
✅ Microsoft Graph
   ✅ User.Read (Delegated) - Granted for [Your Organization]
   ✅ Calendars.ReadWrite (Delegated) - Granted for [Your Organization]
   ✅ offline_access (Delegated) - Granted for [Your Organization]
   ✅ Mail.Send (Delegated) - Granted for [Your Organization]  ← NEW
   ✅ Files.ReadWrite (Delegated) - Granted for [Your Organization]  ← NEW
   ✅ Files.ReadWrite.All (Delegated) - Granted for [Your Organization]  ← NEW (Optional)
   ✅ Sites.ReadWrite.All (Delegated) - Granted for [Your Organization]  ← NEW (Optional)
```

## 🔄 Update Your SCOPE Environment Variable

After adding permissions, update your `SCOPE` environment variable in Render:

```bash
SCOPE=https://graph.microsoft.com/User.Read https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/offline_access
```

Or if you added the optional permissions:

```bash
SCOPE=https://graph.microsoft.com/User.Read https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/Files.ReadWrite.All https://graph.microsoft.com/Sites.ReadWrite.All https://graph.microsoft.com/offline_access
```

## 📝 Detailed Permission Descriptions

### Mail.Send
- **What it does**: Allows the app to send emails on behalf of the signed-in user
- **Required for**: Sending widget exports via Outlook email
- **Security**: User must be authenticated and consent to sending emails

### Files.ReadWrite
- **What it does**: Allows the app to read and write files in the user's OneDrive
- **Required for**: Uploading widget exports (PDF, Word, Excel, PowerPoint) to OneDrive
- **Security**: User must be authenticated and consent to file access

### Files.ReadWrite.All
- **What it does**: Allows the app to read and write all files the user can access
- **When to use**: If Files.ReadWrite doesn't provide enough access
- **Security**: Broader access - use only if needed

### Sites.ReadWrite.All
- **What it does**: Allows the app to read and write items in SharePoint sites
- **When to use**: If you want to upload to SharePoint instead of OneDrive
- **Security**: Requires admin consent

## ⚠️ Important Notes

1. **Admin Consent Required**: All these permissions require admin consent for your organization
2. **User Consent**: Users will see a consent screen when they first authenticate
3. **Token Refresh**: After adding permissions, users may need to re-authenticate to get new tokens with updated scopes
4. **Testing**: Test with a test user account first before rolling out to all users

## 🔍 Troubleshooting

### Permission Not Showing Up
- Make sure you selected "Delegated permissions" (not Application permissions)
- Refresh the page and check again
- Verify you're in the correct app registration

### Admin Consent Not Working
- You must be a Global Administrator or have permission to grant consent
- Check if your organization has consent policies that prevent granting permissions

### Users Getting Permission Errors
- Users may need to re-authenticate to get tokens with new scopes
- Check that admin consent was granted successfully
- Verify the SCOPE environment variable includes all required permissions

## 📚 Additional Resources

- [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Azure AD App Registration Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Admin Consent Workflow](https://learn.microsoft.com/en-us/azure/active-directory/manage-apps/configure-admin-consent-workflow)

