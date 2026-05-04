import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../providers/locale_provider.dart';
import '../providers/ad_provider.dart';
import 'personal_screen.dart';
import 'compatibility_screen.dart';
import 'family_screen.dart';
import 'annual_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Initialize ad SDK in background
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AdProvider>().initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final localeProvider = Provider.of<LocaleProvider>(context);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Align(
                  alignment: Alignment.topRight,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextButton.icon(
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const SettingsScreen()),
                        ),
                        icon: const Icon(Icons.settings, color: Colors.white70, size: 20),
                        label: Text(
                          localeProvider.localeName,
                          style: const TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                const Text(
                  '🔮 Family Translator',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  l10n.tagline,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 60),
                _buildModeCard(
                  context,
                  icon: Icons.person,
                  title: l10n.personalMode,
                  subtitle: l10n.personalModeSubtitle,
                  color: Colors.white,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const PersonalScreen()),
                  ),
                ),
                const SizedBox(height: 16),
                _buildModeCard(
                  context,
                  icon: Icons.favorite,
                  title: l10n.loveMode,
                  subtitle: l10n.loveModeSubtitle,
                  color: Colors.white,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const CompatibilityScreen()),
                  ),
                ),
                const SizedBox(height: 16),
                _buildModeCard(
                  context,
                  icon: Icons.family_restroom,
                  title: l10n.familyMode,
                  subtitle: l10n.familyModeSubtitle,
                  color: Colors.amber.shade100,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const FamilyScreen()),
                  ),
                ),
                const SizedBox(height: 16),
                _buildModeCard(
                  context,
                  icon: Icons.calendar_today,
                  title: '年度運勢',
                  subtitle: '查看這一年的運勢走向與每月重點',
                  color: Colors.white,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const AnnualScreen()),
                  ),
                ),
                const Spacer(),
                Text(
                  l10n.notFortuneTelling,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white54, fontSize: 12),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildModeCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF667EEA).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: const Color(0xFF667EEA), size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }
}
