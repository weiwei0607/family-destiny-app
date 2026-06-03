import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/chart_model.dart';
import '../providers/ad_provider.dart';
import '../services/api_service.dart';

class AnnualScreen extends StatefulWidget {
  const AnnualScreen({super.key});

  @override
  State<AnnualScreen> createState() => _AnnualScreenState();
}

class _AnnualScreenState extends State<AnnualScreen> {
  final _nameController = TextEditingController();
  String _gender = '女';
  final _dateController = TextEditingController(text: '1999-06-07');
  final _timeController = TextEditingController(text: '12:00');
  String _location = 'taipei';
  int _year = DateTime.now().year;

  AnnualReport? _report;
  bool _loading = false;

  Future<void> _generateReport() async {
    if (_nameController.text.trim().isEmpty || _dateController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('請填寫姓名和生日')),
      );
      return;
    }

    // Check premium access before hitting the endpoint
    final adProvider = context.read<AdProvider>();
    adProvider.checkExpiry();
    if (!ApiService().isPremium && !adProvider.isPremiumUnlocked) {
      if (mounted) _showPaywall();
      return;
    }
    if (adProvider.isPremiumUnlocked) ApiService().isPremium = true;

    setState(() => _loading = true);

    try {
      final report = await ApiService().getAnnualReport(
        name: _nameController.text.trim(),
        gender: _gender,
        date: _dateController.text.trim(),
        time: _timeController.text.trim(),
        location: _location,
        year: _year,
        tier: 'standard',
      );

      setState(() {
        _report = report;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      if (e.toString().contains('PREMIUM_REQUIRED')) {
        if (mounted) _showPaywall();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('生成失敗: $e')),
          );
        }
      }
    }
  }

  void _showPaywall() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF1E1E2E),
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.auto_awesome, size: 48, color: Colors.amber),
            const SizedBox(height: 16),
            const Text(
              '年度運勢需要 Premium',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 8),
            const Text(
              'AI 結合五個系統分析整年運勢，屬於付費功能',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white60),
            ),
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: () async {
                Navigator.pop(ctx);
                final adProvider = context.read<AdProvider>();
                await adProvider.watchAdToUnlock(unlockDuration: const Duration(hours: 1));
                if (!mounted) return;
                if (adProvider.isPremiumUnlocked) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('✅ 已解鎖 ${adProvider.timeRemaining}'),
                      backgroundColor: Colors.green,
                    ),
                  );
                  _generateReport();
                }
              },
              icon: const Icon(Icons.play_circle_outline, color: Colors.amber),
              label: const Text('看廣告免費解鎖 1 小時', style: TextStyle(color: Colors.amber)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.amber),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
            if (kDebugMode) ...[
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () {
                  ApiService().isPremium = true;
                  Navigator.pop(ctx);
                  _generateReport();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF667EEA),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                child: const Text('💎 開發者繞過付費牆'),
              ),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _dateController.dispose();
    _timeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0F1A),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text('年度運勢', style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: _report != null ? _buildReportView() : _buildInputForm(),
    );
  }

  Widget _buildInputForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2A1B5C), Color(0xFF4A2C7A)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '📅 年度運勢報告',
                  style: TextStyle(
                    color: Colors.amber,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  '輸入你的出生資料和目標年份，AI 會結合八字流年、占星回歸、人類圖等五個系統，分析這一年的運勢走向。',
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Personal info
          _buildTextField(_nameController, '姓名', Icons.person_outline),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildTextField(_dateController, '生日 (YYYY-MM-DD)', Icons.calendar_today),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildTextField(_timeController, '時間 (HH:MM)', Icons.access_time),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildDropdown(
                  value: _gender,
                  items: const ['男', '女'],
                  onChanged: (v) => setState(() => _gender = v!),
                  label: '性別',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildDropdown(
                  value: _location,
                  items: const ['taipei', 'taichung', 'kaohsiung'],
                  onChanged: (v) => setState(() => _location = v!),
                  label: '地點',
                  itemLabel: (v) => {'taipei': '台北', 'taichung': '台中', 'kaohsiung': '高雄'}[v] ?? v,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Year selector
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E1E2E),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '選擇年份',
                  style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [DateTime.now().year - 1, DateTime.now().year, DateTime.now().year + 1, DateTime.now().year + 2]
                      .map((y) {
                    final isSelected = _year == y;
                    return ChoiceChip(
                      label: Text('$y年'),
                      selected: isSelected,
                      onSelected: (_) => setState(() => _year = y),
                      selectedColor: const Color(0xFF667EEA),
                      backgroundColor: const Color(0xFF2A2A3E),
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : Colors.white.withAlpha(180),
                        fontSize: 13,
                      ),
                      side: BorderSide.none,
                    );
                  }).toList(),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loading ? null : _generateReport,
            icon: _loading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.auto_awesome),
            label: Text(_loading ? '分析中...' : '生成 $_year 年度運勢'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF667EEA),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 30),
        ],
      ),
    );
  }

  Widget _buildReportView() {
    final report = _report!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Hero card
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF6C5DD3), Color(0xFF8B5CF6)],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                Text(
                  '$_year',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withAlpha(30),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    report.yearTheme,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Yearly overview
          _buildSectionCard(
            icon: Icons.menu_book,
            title: '年度概述',
            child: Text(
              report.yearlyOverview,
              style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.7),
            ),
          ),

          // Bazi luck
          if (report.baziLuck.isNotEmpty)
            _buildSectionCard(
              icon: Icons.timeline,
              title: '八字流年',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildInfoRow('流年柱', report.baziLuck['annual_pillar'] ?? ''),
                  const SizedBox(height: 8),
                  _buildInfoRow('運勢方向', report.baziLuck['luck_direction'] ?? ''),
                  const SizedBox(height: 8),
                  _buildInfoRow('五行平衡', report.baziLuck['element_balance'] ?? ''),
                ],
              ),
            ),

          // Opportunities & Challenges
          Row(
            children: [
              Expanded(
                child: _buildSectionCard(
                  icon: Icons.star_border,
                  title: '關鍵機會',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: report.keyOpportunities.map<Widget>((o) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(Icons.check_circle_outline, size: 16, color: Colors.green[300]),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                o.toString(),
                                style: const TextStyle(color: Colors.white70, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSectionCard(
                  icon: Icons.warning_amber_outlined,
                  title: '需要注意',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: report.keyChallenges.map<Widget>((c) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(Icons.error_outline, size: 16, color: Colors.orange[300]),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                c.toString(),
                                style: const TextStyle(color: Colors.white70, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ],
          ),

          // Monthly insights
          if (report.monthlyInsights.isNotEmpty)
            _buildSectionCard(
              icon: Icons.calendar_month,
              title: '每月運勢',
              child: Column(
                children: report.monthlyInsights.map<Widget>((m) {
                  final energyColor = m.energy == 'high'
                      ? Colors.green
                      : m.energy == 'low'
                          ? Colors.orange
                          : Colors.blue;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2A3E),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: energyColor.withAlpha(40),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Center(
                            child: Text(
                              '${m.month}',
                              style: TextStyle(
                                color: energyColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                m.theme,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                m.advice,
                                style: const TextStyle(color: Colors.white60, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: energyColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),

          // Annual prescription
          if (report.annualPrescription.isNotEmpty)
            _buildSectionCard(
              icon: Icons.local_pharmacy_outlined,
              title: '年度處方',
              child: Column(
                children: report.annualPrescription.map<Widget>((p) {
                  return ListTile(
                    leading: Text(p['icon'] ?? '💡', style: const TextStyle(fontSize: 24)),
                    title: Text(
                      p['title'] ?? '',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text(
                      p['description'] ?? '',
                      style: const TextStyle(color: Colors.white70),
                    ),
                    contentPadding: EdgeInsets.zero,
                  );
                }).toList(),
              ),
            ),

          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: () => setState(() => _report = null),
            icon: const Icon(Icons.refresh),
            label: const Text('重新查詢'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF667EEA),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
          const SizedBox(height: 30),
        ],
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String hint, IconData icon) {
    return TextField(
      controller: controller,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: Colors.white.withAlpha(80)),
        prefixIcon: Icon(icon, size: 18, color: Colors.white.withAlpha(100)),
        filled: true,
        fillColor: const Color(0xFF2A2A3E),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      ),
    );
  }

  Widget _buildDropdown({
    required String value,
    required List<String> items,
    required ValueChanged<String?> onChanged,
    required String label,
    String Function(String)? itemLabel,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A3E),
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isExpanded: true,
          dropdownColor: const Color(0xFF2A2A3E),
          style: const TextStyle(color: Colors.white, fontSize: 14),
          icon: Icon(Icons.arrow_drop_down, color: Colors.white.withAlpha(100)),
          hint: Text(label, style: TextStyle(color: Colors.white.withAlpha(80))),
          onChanged: onChanged,
          items: items.map((item) {
            return DropdownMenuItem(
              value: item,
              child: Text(itemLabel?.call(item) ?? item),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildSectionCard({required IconData icon, required String title, required Widget child}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.amber, size: 20),
              const SizedBox(width: 10),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label：',
          style: TextStyle(color: Colors.white.withAlpha(102), fontSize: 13),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(color: Colors.white70, fontSize: 13),
          ),
        ),
      ],
    );
  }
}
