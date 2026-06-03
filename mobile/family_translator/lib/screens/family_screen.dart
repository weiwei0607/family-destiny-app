import 'package:flutter/material.dart';
import '../models/chart_model.dart';
import '../services/api_service.dart';

class FamilyScreen extends StatefulWidget {
  const FamilyScreen({super.key});

  @override
  State<FamilyScreen> createState() => _FamilyScreenState();
}

class _FamilyScreenState extends State<FamilyScreen> {
  final List<_MemberForm> _members = [];
  FamilyReport? _report;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    // Add two default members
    _addMember(role: 'father');
    _addMember(role: 'mother');
  }

  void _addMember({String role = 'child'}) {
    setState(() {
      _members.add(_MemberForm(
        nameController: TextEditingController(),
        dateController: TextEditingController(text: '1990-01-01'),
        timeController: TextEditingController(text: '12:00'),
        gender: '男',
        role: role,
        location: 'taipei',
      ));
    });
  }

  void _removeMember(int index) {
    if (_members.length <= 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('至少需要兩位家庭成員')),
      );
      return;
    }
    setState(() {
      _members[index].dispose();
      _members.removeAt(index);
    });
  }

  Future<void> _generateReport() async {
    // Validate
    for (final m in _members) {
      if (m.nameController.text.trim().isEmpty ||
          m.dateController.text.trim().isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('請填寫所有成員的姓名和生日')),
        );
        return;
      }
    }

    setState(() => _loading = true);

    try {
      final memberData = _members.map((m) => {
        'name': m.nameController.text.trim(),
        'gender': m.gender,
        'date': m.dateController.text.trim(),
        'time': m.timeController.text.trim(),
        'location': m.location,
        'role': m.role,
      }).toList();

      final report = await ApiService().getFamilyReport(
        members: memberData,
        tier: 'standard',
      );

      setState(() {
        _report = report;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('生成失敗: $e')),
      );
    }
  }

  @override
  void dispose() {
    for (final m in _members) {
      m.dispose();
    }
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
        title: const Text('家庭合盤', style: TextStyle(fontWeight: FontWeight.w600)),
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
                  '👨‍👩‍👧‍👦 家庭合盤',
                  style: TextStyle(
                    color: Colors.amber,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  '輸入家庭成員的資料，AI 會分析每個人在家庭中的獨特角色，以及成員之間的互動動力學。',
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          ..._members.asMap().entries.map((entry) {
            return _buildMemberCard(entry.key, entry.value);
          }),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => _addMember(),
            icon: const Icon(Icons.add, color: Colors.amber),
            label: const Text('新增成員', style: TextStyle(color: Colors.amber)),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: Colors.amber),
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: _loading ? null : _generateReport,
            icon: _loading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.auto_awesome),
            label: Text(_loading ? '分析中...' : '生成家庭合盤'),
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

  Widget _buildMemberCard(int index, _MemberForm member) {
    final roleLabels = {
      'father': '爸爸',
      'mother': '媽媽',
      'child': '孩子',
      'grandparent': '祖父母',
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
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
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.amber.withAlpha(30),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '成員 ${index + 1}',
                  style: const TextStyle(color: Colors.amber, fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ),
              const Spacer(),
              if (_members.length > 2)
                IconButton(
                  onPressed: () => _removeMember(index),
                  icon: const Icon(Icons.delete_outline, color: Colors.redAccent, size: 20),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
            ],
          ),
          const SizedBox(height: 12),
          _buildTextField(member.nameController, '姓名', Icons.person_outline),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _buildTextField(member.dateController, '生日 (YYYY-MM-DD)', Icons.calendar_today),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildTextField(member.timeController, '時間 (HH:MM)', Icons.access_time),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _buildDropdown(
                  value: member.gender,
                  items: const ['男', '女'],
                  onChanged: (v) => setState(() => member.gender = v!),
                  label: '性別',
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildDropdown(
                  value: member.role,
                  items: roleLabels.keys.toList(),
                  onChanged: (v) => setState(() => member.role = v!),
                  label: '角色',
                  itemLabel: (v) => roleLabels[v] ?? v,
                ),
              ),
            ],
          ),
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
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
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

  Widget _buildReportView() {
    final report = _report!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF6C5DD3), Color(0xFF8B5CF6)],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                const Icon(Icons.home, color: Colors.white, size: 40),
                const SizedBox(height: 12),
                const Text(
                  '家庭合盤分析',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${_members.length} 人家庭 · 五系統分析',
                  style: TextStyle(color: Colors.white.withAlpha(180), fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Family narrative
          _buildSectionCard(
            icon: Icons.menu_book,
            title: '家庭敘事',
            child: Text(
              report.familyNarrative,
              style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.7),
            ),
          ),

          // Member reports
          _buildSectionCard(
            icon: Icons.people_outline,
            title: '每個人的家庭角色',
            child: Column(
              children: report.memberReports.map<Widget>((m) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2A2A3E),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            m['name'] ?? '',
                            style: const TextStyle(
                              color: Colors.amber,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.amber.withAlpha(30),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              m['family_role'] ?? '',
                              style: const TextStyle(color: Colors.amber, fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        m['chart_summary'] ?? '',
                        style: TextStyle(color: Colors.white.withAlpha(180), fontSize: 13),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),

          // Relationship matrix
          if (report.relationshipMatrix.isNotEmpty)
            _buildSectionCard(
              icon: Icons.account_tree_outlined,
              title: '關係動力學',
              child: Column(
                children: report.relationshipMatrix.map<Widget>((r) {
                  final pair = r['pair'] as List? ?? [];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2A3E),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${pair.isNotEmpty ? pair[0] : ''} ↔ ${pair.length > 1 ? pair[1] : ''}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          r['dynamic'] ?? '',
                          style: const TextStyle(color: Colors.white70, fontSize: 14),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Icon(Icons.thumb_up_outlined, size: 14, color: Colors.green[300]),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                r['strength'] ?? '',
                                style: TextStyle(color: Colors.green[200], fontSize: 12),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(Icons.warning_amber_outlined, size: 14, color: Colors.orange[300]),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                r['watch_out'] ?? '',
                                style: TextStyle(color: Colors.orange[200], fontSize: 12),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),

          // Communication guide
          if (report.communicationGuide.isNotEmpty)
            _buildSectionCard(
              icon: Icons.chat_bubble_outline,
              title: '溝通指南',
              child: Column(
                children: report.communicationGuide.entries.map<Widget>((entry) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 4,
                          height: 4,
                          margin: const EdgeInsets.only(top: 8, right: 10),
                          decoration: const BoxDecoration(
                            color: Colors.amber,
                            shape: BoxShape.circle,
                          ),
                        ),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                entry.key,
                                style: const TextStyle(
                                  color: Colors.amber,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                entry.value.toString(),
                                style: const TextStyle(color: Colors.white70, fontSize: 13),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),

          // Family prescription
          if (report.familyPrescription.isNotEmpty)
            _buildSectionCard(
              icon: Icons.local_pharmacy_outlined,
              title: '家庭處方',
              child: Column(
                children: report.familyPrescription.map<Widget>((p) {
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
            label: const Text('重新分析'),
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
}

class _MemberForm {
  final TextEditingController nameController;
  final TextEditingController dateController;
  final TextEditingController timeController;
  String gender;
  String role;
  String location;

  _MemberForm({
    required this.nameController,
    required this.dateController,
    required this.timeController,
    required this.gender,
    required this.role,
    required this.location,
  });

  void dispose() {
    nameController.dispose();
    dateController.dispose();
    timeController.dispose();
  }
}
