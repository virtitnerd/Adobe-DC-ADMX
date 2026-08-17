<p align="center"><a href="https://buymeacoffee.com/systmworks"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="45" alt="Buy me a coffee"></a></p>

> I have spent many, many hours creating and testing this ADMX. If it helps you please consider buying me a Coffee :)

# AdobeDC ADMX - Combined Machine + User

**Current version: v3.5** (22 July 2026). Full version history: [GitHub Releases](https://github.com/virtitnerd/Adobe-DC-ADMX/releases).

**Current production release.** Supersedes the separate machine template (v2.21) and user template ([Adobe-DC-User-ADMX v1.10](https://github.com/systmworks/Adobe-DC-User-ADMX)) for new Group Policy and Intune deployments.

> [!IMPORTANT]
> **Stable upgrade path (v3.4+).** From v3.4 onward, releases are **additive-only** except where a release note documents a one-time control-type correction. Re-uploading `AdobeDC.admx` + ADML preserves existing Intune/GPO bindings for all other settings. Deleting the imported ADMX in Intune before re-upload is still required (platform limitation for custom ADMX).

> [!WARNING]
> **Breaking change when migrating from v2.x or User ADMX v1.x.** Combined v3.0+ uses namespace `Adobe.Policies.AdobeDC` and a re-organised policy tree. **Intune ADMX policy backups / exports taken against v2.x (or the separate User ADMX v1.x) will not import** - the `definitionId` GUIDs and category paths no longer match. To migrate an existing v2.x export, run [`Helper_Scripts/Convert-AdobeDcIntuneExportToCombinedV3.ps1`](../Helper_Scripts/Convert-AdobeDcIntuneExportToCombinedV3.ps1) to convert it to the combined layout before re-importing. See [Migrating from v2.21 + User v1.10](#migrating-from-v221--user-v110).

> [!NOTE]
> **Upgrading from any combined v3.x release** keeps the same namespace and policy `name` attributes for all settings present in that version. Re-upload `AdobeDC.admx` + ADML. Check the [release notes](https://github.com/virtitnerd/Adobe-DC-ADMX/releases) for the target version to identify any control-type corrections that require one-time re-selection in Intune/GPO.

## What is in the combined template

| Area | Detail |
|------|--------|
| **Packaging** | Single `AdobeDC.admx`/ADML pair for **Computer + User** configuration under one namespace |
| **Policy inventory** | **834** policies — **319** machine + **515** user (ADMX `<policy>` entries; see note below) |
| **Namespace** | `Adobe.Policies.AdobeDC` (replaces separate `Adobe.Policies.Adobe_User` user namespace) |
| **Computer tree** | **Adobe DC** → **Acrobat & Reader DC** / **Reader DC (32-bit)** / **Non-Policy Settings** / **Web Browser Extension** |
| **User tree** | **Adobe DC** → **Acrobat DC** / **Reader DC** |
| **OS requirement** | **64-bit Windows (x64) only.** The 32-bit application policies (Reader DC 32-bit, Acrobat DC 32-bit) configure 32-bit Adobe products running on a 64-bit OS — they rely on the `WOW6432Node` registry hive, which only exists on 64-bit Windows. Genuine 32-bit Windows is not supported. |
| **De-duplication** | `HKLM\SOFTWARE\Policies` settings emit once per product hive (no redundant `WOW6432Node\Policies` copies) |
| **Sources** | Device v2.21 + User v1.10 + Browser Extension schema.json |

**Policy count note:** **831** is the number of configurable policy entries in the ADMX (what Intune and GPMC show). **306** machine includes architecture-specific non-policy settings emitted separately for x64 and x86, plus 12 Web Browser Extension policies (Chrome + Edge). There are **155** unique machine settings in the source reference (**117** apply to both Reader and Acrobat; `tBuiltInPermList` is excluded as REG_BINARY). Product-scoped tables in [Documentation](../README.md) list user and machine settings because shared settings appear under each product.

### Built-in Attachment Permissions List (`tBuiltInPermList`)

This is the **only** REG_BINARY setting in the template. ADMX/ADML has **no binary element type**, so it cannot be authored via Group Policy or Intune ADMX upload. Combined v3.1 incorrectly used a text box (REG_SZ); v3.2 removed the policy.

Deploy the attachment allow/block list using [`Helper_Scripts/Set-AdobeBuiltInPermList.ps1`](../Helper_Scripts/Set-AdobeBuiltInPermList.ps1) (**`-ImportHex`** from `-ExportHex` is the trusted path; `-PermList` is best-effort), Group Policy Preferences registry items, or Intune custom OMA-URI with bytes captured from Acrobat Trust Manager.

### Migrating from v2.21 + User v1.10

Because the initial combined release (v3.0) is a breaking change (see the warning above), existing Intune ADMX policy exports/backups cannot be re-imported as-is. Convert them first:

| Step | Action |
|------|--------|
| 1 | Convert any v2.x Intune export/backup JSON with [`Helper_Scripts/Convert-AdobeDcIntuneExportToCombinedV3.ps1`](../Helper_Scripts/Convert-AdobeDcIntuneExportToCombinedV3.ps1) - it remaps category paths, de-duplicates redundant Policies-branch entries, and clears stale `definitionId` GUIDs (outputs `*_combined-v3.json`) |
| 2 | Remove existing `Adobe.Policies.AdobeDC` **and** `Adobe.Policies.Adobe_User` ADMX imports from Intune (wait 2-5 minutes after deletion) |
| 3 | Upload `AdobeDC.admx` and `en-US/AdobeDC.adml` from this folder |
| 4 | Import the converted `*_combined-v3.json` and re-bind / re-assign the policy settings |

If you migrated Intune exports from v2.19, Reader-only x64 upsell settings already map to Unified x64 - they will bind after uploading this ADMX.

## Files

| File | Scope | Policies |
|------|-------|----------|
| `AdobeDC.admx` + `en-US/AdobeDC.adml` | Machine + User | **834** (319 machine + 515 user) |

*319 machine = ADMX policy entries (includes 12 Web Browser Extension policies, 2 Machine-scope URL Access Permissions policies, 8 ARM Legacy updater policies, and 5 Azure AD/federated sign-in + Reader Protected View + Reader promotional campaign policies); 155 unique machine settings from Adobe PrefRef; product-scoped reference tables total 125 Reader + 172 Acrobat.*

Published policy reference tables: [Documentation](../README.md).

## Namespace

| Attribute | Value |
|-----------|-------|
| Prefix | `AdobeDC` |
| Namespace URI | `Adobe.Policies.AdobeDC` |
| ADMX / ADML `revision` | 3.4 |
| `minRequiredRevision` (`resources`) | 3.4 |

## Intune upload

1. **Remove** any existing ADMX entry for `Adobe.Policies.AdobeDC` and `Adobe.Policies.Adobe_User` before uploading - including failed or stuck imports.
2. Wait 2-5 minutes after deletion.
3. Upload `AdobeDC.admx` and `en-US/AdobeDC.adml` together.
4. Assign machine settings to a **device group**; assign user settings to a **user group** (or combine both in one profile - scope is determined by each policy's `class` attribute).
5. After upgrading, re-select any settings whose control type changed in that release. See the [release notes](https://github.com/virtitnerd/Adobe-DC-ADMX/releases) for the target version for the specific list.

## Group Policy

Copy `AdobeDC.admx` to `%SystemRoot%\PolicyDefinitions` and `AdobeDC.adml` to `%SystemRoot%\PolicyDefinitions\en-US`, then run `gpupdate /force`. Machine policies appear under **Computer Configuration**; user policies under **User Configuration**.

Full release history: [GitHub Releases](https://github.com/virtitnerd/Adobe-DC-ADMX/releases).

---

**Sharing & responsibility** - Built for the community, shared with good intentions. Use at your own risk. The author accepts no responsibility for any outcomes resulting from the use of these files. Always verify registry paths and values, and test in a safe environment first. If you find an issue or have a suggestion, contributions are welcome.
