import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/chart_model.dart';
import '../services/api_service.dart';
import '../providers/ad_provider.dart';

class CompatibilityReportScreen extends StatefulWidget {
  final Map<String, dynamic> person1;
  final Map<String, dynamic> person2;

  const CompatibilityReportScreen({
    super.key,
    required this.person1,
    required this.person2,
  });

  @override
  State<CompatibilityReportScreen> createState() => _CompatibilityReportScreenState();
}

class _CompatibilityReportScreenState extends State<CompatibilityReportScreen> {
  BasicCompatibility? _basicCompat;
  DeepCompatibility? _deepCompat;
  bool _loadingBasic = true;
  bool _loadingPremium = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadBasicCompatibility();
  }

  Future<void> _loadBasicCompatibility() async {
    try {
      final result = await ApiService().getBasicCompatibility(
        person1: widget.person1,
        person2: widget.person2,
      );
      setState(() {
        _basicCompat = result;
        _loadingBasic = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingBasic = false;
      });
    }
  }

  Future<void> _unlockDeepReport({String tier = 'standard'}) async {
    // Check if ad-unlocked premium is active
    final adProvider = context.read<AdProvider>();
    adProvider.checkExpiry();
    if (adProvider.isPremiumUnlocked) {
      ApiService().isPremium = true;
    }

    setState(() => _loadingPremium = true);
    try {
      final result = await ApiService().getDeepCompatibility(
        person1: widget.person1,
        person2: widget.person2,
        tier: tier,
      );
      setState(() {
        _deepCompat = result;
        _loadingPremium = false;
      });
    } catch (e) {
      setState(() => _loadingPremium = false);
      if (!mounted) return;
      if (e.toString().contains('PREMIUM_REQUIRED')) {
        _showPaywall();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('載入失敗: $e')),
        );
      }
    }
  }

  void _showPaywall() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.lock, size: 48, color: Color(0xFF667EEA)),
            const SizedBox(height: 16),
            const Text(
              '解鎖我們的關係密碼',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              '免費版只能看到分數，選一個適合你們的方案',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            _buildTierOption(
              price: 'NT\$30',
              label: 'Lite',
              badge: '先試試',
              desc: '關係敘事 200 字——了解你們像什麼',
              color: Colors.grey.shade100,
              onTap: () {
                Navigator.pop(context);
                _unlockDeepReport(tier: 'lite');
              },
            ),
            const SizedBox(height: 12),
            _buildTierOption(
              price: 'NT\$99',
              label: 'Standard',
              badge: '最熱門',
              desc: '敘事 + 衝突點 + 溝通指南',
              color: const Color(0xFF667EEA).withValues(alpha: 0.08),
              borderColor: const Color(0xFF667EEA),
              onTap: () {
                Navigator.pop(context);
                _unlockDeepReport(tier: 'standard');
              },
            ),
            const SizedBox(height: 12),
            _buildTierOption(
              price: 'NT\$199',
              label: 'Premium',
              badge: '最完整',
              desc: '全部內容 + 關係處方籤 + 30天成長計畫',
              color: Colors.amber.shade50,
              borderColor: Colors.amber,
              onTap: () {
                Navigator.pop(context);
                _unlockDeepReport(tier: 'premium');
              },
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () async {
                Navigator.pop(context);
                final adProvider = context.read<AdProvider>();
                await adProvider.watchAdToUnlock(unlockDuration: const Duration(hours: 1));
                if (!context.mounted) return;
                if (adProvider.isPremiumUnlocked) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('✅ 已解鎖 ${adProvider.timeRemaining}'),
                      backgroundColor: Colors.green,
                    ),
                  );
                  _unlockDeepReport(tier: 'standard');
                }
              },
              icon: const Icon(Icons.play_circle_outline, color: Color(0xFF667EEA)),
              label: const Text('看廣告免費解鎖 1 小時'),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF667EEA),
                side: const BorderSide(color: Color(0xFF667EEA)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                ApiService().isPremium = true;
                Navigator.pop(context);
                _unlockDeepReport(tier: 'premium');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF667EEA),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('💎 開發者繞過付費牆'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTierOption({
    required String price,
    required String label,
    required String badge,
    required String desc,
    required Color color,
    Color? borderColor,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: borderColor ?? Colors.grey.shade300,
            width: borderColor != null ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(12),
          color: color,
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        price,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF667EEA),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: (borderColor ?? const Color(0xFF667EEA)).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          badge,
                          style: TextStyle(
                            fontSize: 11,
                            color: borderColor ?? const Color(0xFF667EEA),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    label,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    desc,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingBasic) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('錯誤')),
        body: Center(child: Text(_error!)),
      );
    }

    final compat = _basicCompat!;

    return Scaffold(
      appBar: AppBar(
        title: const Text('💕 合盤結果'),
        backgroundColor: const Color(0xFF667EEA),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Score card
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Text(
                    compat.stars,
                    style: const TextStyle(fontSize: 40),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '「${compat.summary}」',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 18,
                      color: Colors.white,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '綜合評分: ${compat.overallScore}/5.0',
                    style: const TextStyle(color: Colors.white70),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // Dimensions
            const Text(
              '五維度分析',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...compat.dimensions.entries.map((e) {
              final data = e.value as Map<String, dynamic>;
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  title: Text(_dimensionName(e.key)),
                  subtitle: Text(data['note'] ?? ''),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: List.generate(
                      data['score'] ?? 0,
                      (_) => const Icon(Icons.star, color: Colors.amber, size: 20),
                    ),
                  ),
                ),
              );
            }),
            const SizedBox(height: 24),
            // Person summaries
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('👤 ${widget.person1['name'] ?? '你'}: ${compat.person1Summary}'),
                    const SizedBox(height: 8),
                    Text('💕 ${widget.person2['name'] ?? '對方'}: ${compat.person2Summary}'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            // Deep report section
            if (_deepCompat == null) ...[
              _buildDeepReportTeaser(compat),
            ] else ...[
              _buildDeepReportSection(),
            ],
          ],
        ),
      ),
    );
  }

  String _dimensionName(String key) {
    final names = {
      'bazi': '八字',
      'astro': '占星',
      'ziwei': '紫微',
      'hd': '人類圖',
      'xingxiu': '星宿',
    };
    return names[key] ?? key;
  }

  Widget _buildDeepReportTeaser(BasicCompatibility basic) {
    final summary = basic.summary;
    final score = basic.overallScore;
    final p1 = widget.person1['name'] ?? '你';
    final p2 = widget.person2['name'] ?? '對方';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Blurred preview
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Color(0xFF667EEA)),
                  const SizedBox(width: 8),
                  const Text(
                    '關係敘事預覽',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.lock, size: 14, color: Colors.amber.shade800),
                        const SizedBox(width: 4),
                        Text(
                          '付費解鎖',
                          style: TextStyle(fontSize: 12, color: Colors.amber.shade800),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                '你們的基礎合盤分數是 $score 分——$summary。這個分數背後，是兩個獨立靈魂在五個維度上的交會與摩擦。想知道為什麼你們會這樣互動？為什麼有些地方特別舒服、有些地方特別卡？深度報告會告訴你們的關係動力學...',
                style: const TextStyle(fontSize: 15, height: 1.6),
              ),
              const SizedBox(height: 8),
              Container(
                height: 60,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [Colors.grey.shade50.withValues(alpha: 0), Colors.grey.shade50],
                  ),
                ),
                child: const Center(
                  child: Icon(Icons.keyboard_arrow_down, color: Colors.grey),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Locked content list
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.amber.shade50,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.amber.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                '深度報告還包含',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber.shade900,
                ),
              ),
              const SizedBox(height: 12),
              _buildLockedItem(
                icon: Icons.favorite_border,
                title: '關係敘事',
                desc: '你們的關係像什麼？為什麼會互相吸引又互相摩擦？',
              ),
              _buildLockedItem(
                icon: Icons.warning_amber_outlined,
                title: '衝突點解析',
                desc: '2-3 個具體的衝突點——「當 $p1 生氣時，$p2 會...」',
              ),
              _buildLockedItem(
                icon: Icons.chat_bubble_outline,
                title: '溝通指南',
                desc: '當你生氣時怎麼辦、當對方生氣時怎麼辦、最好的溝通時機',
              ),
              _buildLockedItem(
                icon: Icons.local_pharmacy_outlined,
                title: '關係處方籤',
                desc: '約會 / 聊天 / 共同活動 / 旅行——具體行動建議',
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadingPremium ? null : _unlockDeepReport,
                icon: _loadingPremium
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.lock_open),
                label: Text(_loadingPremium ? '生成中...' : '解鎖我們的關係密碼'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF667EEA),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLockedItem({
    required IconData icon,
    required String title,
    required String desc,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: const Color(0xFF667EEA)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                    Icon(Icons.lock_outline, size: 16, color: Colors.grey.shade400),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  desc,
                  style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeepReportSection() {
    final deep = _deepCompat!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.favorite, color: Colors.white),
                  SizedBox(width: 8),
                  Text(
                    '關係敘事',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                deep.relationshipNarrative,
                style: const TextStyle(fontSize: 15, color: Colors.white, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          '衝突點',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...deep.conflictPoints.map((p) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: const Icon(Icons.warning_amber, color: Colors.orange),
            title: Text(p.toString()),
          ),
        )),
        const SizedBox(height: 24),
        const Text(
          '溝通指南',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...deep.communicationGuide.entries.map((e) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            title: Text(e.key),
            subtitle: Text(e.value.toString()),
          ),
        )),
        const SizedBox(height: 24),
        const Text(
          '關係處方籤',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...deep.prescription.map((p) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Text(p['icon'] ?? '💕', style: const TextStyle(fontSize: 24)),
            title: Text(p['title'] ?? ''),
            subtitle: Text(p['description'] ?? ''),
          ),
        )),
      ],
    );
  }
}
