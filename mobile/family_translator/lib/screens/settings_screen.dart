import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../providers/locale_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final localeProvider = Provider.of<LocaleProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.settings),
        backgroundColor: const Color(0xFF667EEA),
        foregroundColor: Colors.white,
      ),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.language, color: Color(0xFF667EEA)),
            title: Text(l10n.language),
            subtitle: Text(localeProvider.localeName),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _showLanguagePicker(context, localeProvider),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline, color: Color(0xFF667EEA)),
            title: const Text('Family Translator'),
            subtitle: Text(l10n.notFortuneTelling),
          ),
        ],
      ),
    );
  }

  void _showLanguagePicker(BuildContext context, LocaleProvider provider) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              AppLocalizations.of(context)!.language,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            _LanguageTile(
              label: '繁體中文',
              subtitle: 'Traditional Chinese',
              selected: provider.langCode == 'zh-TW',
              onTap: () {
                provider.setLocale(const Locale('zh', 'TW'));
                Navigator.pop(ctx);
              },
            ),
            _LanguageTile(
              label: '简体中文',
              subtitle: 'Simplified Chinese',
              selected: provider.langCode == 'zh-CN',
              onTap: () {
                provider.setLocale(const Locale('zh', 'CN'));
                Navigator.pop(ctx);
              },
            ),
            _LanguageTile(
              label: 'English',
              subtitle: '英文',
              selected: provider.langCode == 'en',
              onTap: () {
                provider.setLocale(const Locale('en'));
                Navigator.pop(ctx);
              },
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _LanguageTile extends StatelessWidget {
  final String label;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;

  const _LanguageTile({
    required this.label,
    required this.subtitle,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: selected
          ? const Icon(Icons.check_circle, color: Color(0xFF667EEA))
          : const Icon(Icons.circle_outlined, color: Colors.grey),
      title: Text(label),
      subtitle: Text(subtitle, style: TextStyle(color: Colors.grey.shade600)),
      onTap: onTap,
    );
  }
}
