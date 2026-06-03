import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/chart_model.dart';
import '../services/api_service.dart';
import '../providers/ad_provider.dart';
import 'ask_screen.dart';

class PersonalReportScreen extends StatefulWidget {
  final String name;
  final String gender;
  final String date;
  final String time;
  final String location;

  const PersonalReportScreen({
    super.key,
    required this.name,
    required this.gender,
    required this.date,
    required this.time,
    required this.location,
  });

  @override
  State<PersonalReportScreen> createState() => _PersonalReportScreenState();
}

class _PersonalReportScreenState extends State<PersonalReportScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  BasicChart? _basicChart;
  FullReport? _fullReport;
  bool _loadingBasic = true;
  bool _loadingPremium = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadBasicChart();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadBasicChart() async {
    try {
      final chart = await ApiService().getBasicChart(
        name: widget.name,
        gender: widget.gender,
        date: widget.date,
        time: widget.time,
        location: widget.location,
      );
      setState(() {
        _basicChart = chart;
        _loadingBasic = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loadingBasic = false;
      });
    }
  }

  Future<void> _unlockFullReport({String tier = 'standard'}) async {
    // Check if ad-unlocked premium is active
    final adProvider = context.read<AdProvider>();
    adProvider.checkExpiry();
    if (adProvider.isPremiumUnlocked) {
      // Temporarily enable premium API access
      ApiService().isPremium = true;
    }

    setState(() => _loadingPremium = true);
    try {
      final report = await ApiService().getFullReport(
        name: widget.name,
        gender: widget.gender,
        date: widget.date,
        time: widget.time,
        location: widget.location,
        tier: tier,
      );
      setState(() {
        _fullReport = report;
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
              '看看完整的你',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              '基礎盤免費看完了，選一個適合你的方案',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            _buildTierOption(
              price: 'NT\$30',
              label: 'Lite',
              badge: '先試試',
              desc: '整合畫像 + 人生課題一句話',
              color: Colors.grey.shade100,
              onTap: () {
                Navigator.pop(context);
                _unlockFullReport(tier: 'lite');
              },
            ),
            const SizedBox(height: 12),
            _buildTierOption(
              price: 'NT\$99',
              label: 'Standard',
              badge: '最熱門',
              desc: '整合畫像 + 優缺點 + 課題 + 3條處方',
              color: const Color(0xFF667EEA).withValues(alpha: 0.08),
              borderColor: const Color(0xFF667EEA),
              onTap: () {
                Navigator.pop(context);
                _unlockFullReport(tier: 'standard');
              },
            ),
            const SizedBox(height: 12),
            _buildTierOption(
              price: 'NT\$299',
              label: 'Premium 月訂閱',
              badge: '最划算',
              desc: '全部內容 + 5條處方 + PDF + 無限次',
              color: Colors.amber.shade50,
              borderColor: Colors.amber,
              onTap: () {
                Navigator.pop(context);
                _unlockFullReport(tier: 'premium');
              },
            ),
            const SizedBox(height: 16),
            // Watch ad to unlock
            OutlinedButton.icon(
              onPressed: () async {
                Navigator.pop(context);
                final adProvider = context.read<AdProvider>();
                await adProvider.watchAdToUnlock(unlockDuration: const Duration(hours: 1));
                if (!context.mounted) return;
                if (adProvider.isPremiumUnlocked) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('✅ 已解鎖 ${adProvider.timeRemaining}，可以免費看完整報告'),
                      backgroundColor: Colors.green,
                    ),
                  );
                  _unlockFullReport(tier: 'standard');
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
            if (kDebugMode) ...[
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  ApiService().isPremium = true;
                  Navigator.pop(context);
                  _unlockFullReport(tier: 'premium');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF667EEA),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('💎 開發者繞過付費牆'),
              ),
            ],
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
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.cloud_off, size: 48, color: Colors.grey),
                const SizedBox(height: 16),
                Text(_error!, textAlign: TextAlign.center),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    setState(() {
                      _error = null;
                      _loadingBasic = true;
                    });
                    _loadBasicChart();
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('重試'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final chart = _basicChart!;

    return Scaffold(
      appBar: AppBar(
        title: Text(chart.name.isEmpty ? '我的命盤' : '${chart.name} 的命盤'),
        backgroundColor: const Color(0xFF667EEA),
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: '總覽'),
            Tab(text: '八字'),
            Tab(text: '占星'),
            Tab(text: '紫微'),
            Tab(text: '人類圖'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(chart),
          _buildBaziTab(chart),
          _buildAstroTab(chart),
          _buildZiweiTab(chart),
          _buildHDTab(chart),
        ],
      ),
    );
  }

  // ---------- Free content: basic insights ----------

  Widget _buildOverviewTab(BasicChart chart) {
    return SingleChildScrollView(
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
                  '${chart.energyScore}',
                  style: const TextStyle(
                    fontSize: 56,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Text(
                  '能量指數',
                  style: TextStyle(color: Colors.white70),
                ),
                const SizedBox(height: 12),
                Text(
                  chart.summary,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${chart.xingxiu}宿',
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          // Free insight cards with interpretations
          _buildFragmentCard(
            icon: '⚔️',
            title: '${chart.bazi['day_master']}日主',
            system: '八字',
            trait: chart.interpretations['bazi']?['day_master_trait'] ?? _dayMasterHint(chart.bazi['day_master'] ?? ''),
            lockedItems: const ['五行能量調性', '與其他系統的關聯'],
            color: Colors.blue,
          ),
          _buildFragmentCard(
            icon: '🌞',
            title: '太陽${chart.astrology['太陽']?['sign'] ?? ''}',
            system: '占星',
            trait: chart.interpretations['astrology']?['sun_sign_trait'] ?? _sunSignHint(chart.astrology['太陽']?['sign'] ?? ''),
            lockedItems: const ['月亮星座的內在需求', '上升星座的外在面具'],
            color: Colors.orange,
          ),
          _buildFragmentCard(
            icon: '⚡',
            title: chart.humandesign['energy_type'] ?? '',
            system: '人類圖',
            trait: chart.interpretations['humandesign']?['type_trait'] ?? _hdHint(chart.humandesign['energy_type'] ?? ''),
            lockedItems: const ['人生策略與能量運作', '內在權威與決策方式'],
            color: Colors.purple,
          ),
          _buildFragmentCard(
            icon: '🏠',
            title: '${chart.xingxiu}宿',
            system: '星宿',
            trait: chart.interpretations['xingxiu']?['trait'] ?? _xingxiuHint(chart.xingxiu),
            lockedItems: const ['星宿關係模式', '與其他系統的互動'],
            color: Colors.teal,
          ),
          const SizedBox(height: 20),
          // Premium section
          if (_fullReport == null) ...[
            _buildPremiumTeaser(chart),
          ] else ...[
            _buildFullReportSection(),
          ],
        ],
      ),
    );
  }

  Widget _buildFragmentCard({
    required String icon,
    required String title,
    required String system,
    required String trait,
    required List<String> lockedItems,
    required MaterialColor color,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.shade900.withAlpha(80), color.shade900.withAlpha(40)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.shade700.withAlpha(100)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(icon, style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 10),
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: color.shade800.withAlpha(60),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    system,
                    style: TextStyle(color: color.shade200, fontSize: 11),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              trait,
              style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.6),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.black.withAlpha(40),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.lock_outline, size: 14, color: color.shade300.withAlpha(180)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      lockedItems.join(' · '),
                      style: TextStyle(
                        color: color.shade300.withAlpha(180),
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _dayMasterHint(String dm) {
    final hints = {
      '甲': '大樹人格——向上、正直、有領導氣質',
      '乙': '藤蔓人格——柔韌、適應力強、善於借力',
      '丙': '太陽人格——熱情、照亮別人、需要舞台',
      '丁': '燭火人格——溫暖、細膩、專注而深刻',
      '戊': '高山人格——穩重、可靠、承載力強',
      '己': '田土人格——包容、滋養、默默付出',
      '庚': '刀劍人格——果斷、剛毅、保護弱者',
      '辛': '珠寶人格——精緻、敏銳、追求完美',
      '壬': '大海人格——智慧、流動、深不可測',
      '癸': '雨露人格——溫柔、滲透、潤物無聲',
    };
    return hints[dm] ?? '獨特的五行能量';
  }

  String _sunSignHint(String sign) {
    final hints = {
      '牡羊': '行動派——衝勁十足、不喜歡拖泥帶水',
      '金牛': '穩定派——重視安全感、享受當下',
      '雙子': '溝通者——好奇心強、思維跳躍',
      '巨蟹': '守護者——情感細膩、重視家庭',
      '獅子': '表演者——需要舞台、天生有光',
      '處女': '分析者——追求完美、注重細節',
      '天秤': '協調者——重視和諧、善於社交',
      '天蠍': '洞察者——直覺強烈、愛恨分明',
      '射手': '探索者——熱愛自由、樂觀開朗',
      '摩羯': '建構者——目標導向、踏實努力',
      '水瓶': '革新者——獨特立場、前瞻思維',
      '雙魚': '夢想家——想像力豐富、邊界模糊',
    };
    return hints[sign] ?? '獨特的星座能量';
  }

  String _hdHint(String type) {
    final hints = {
      '顯示生產者': '薦骨能量充沛——回應後出擊、執行力超強',
      '生產者': '持續輸出型——等待邀請、專注深耕',
      '顯示者': '發起型——先知先覺、需要告知',
      '投射者': '引導型——洞察全局、等待認可',
      '反映者': '鏡子型——反映環境、月亮週期決策',
    };
    return hints[type] ?? '獨特的能量運作方式';
  }

  String _xingxiuHint(String xx) {
    final hints = {
      '角': '東方青龍之首——開創、領導、有衝勁',
      '亢': '青龍之頸——自尊、原則、不善妥協',
      '氐': '青龍之胸——根基、穩定、重視家庭',
      '房': '青龍之腹——溫暖、包容、善於照顧',
      '心': '青龍之心——敏感、熱情、情緒豐富',
      '尾': '青龍之尾——堅持、尾聲、有始有終',
      '箕': '青龍之箕——灑脫、風塵、不拘小節',
      '斗': '北方玄武——蓄積、收藏、內在豐富',
      '牛': '玄武之牛——勤奮、踏實、默默承擔',
      '女': '玄武之女——細膩、手藝、追求完美',
      '虛': '玄武之虛——空靈、理想、不易捉摸',
      '危': '玄武之危——危機意識、變通、峰迴路轉',
      '室': '玄武之室——庇護、建構、家的意識',
      '壁': '玄武之壁——防護、界線、支撐他人',
      '奎': '西方白虎——文書、學問、追求完美',
      '婁': '白虎之婁——聚攏、整理、善於歸納',
      '胃': '白虎之胃——儲存、消化、重視累積',
      '昴': '白虎之昴——純淨、潔癖、難以妥協',
      '畢': '白虎之畢——完成、守成、有始有終',
      '觜': '白虎之觜——尖銳、挑剔、洞察細節',
      '參': '白虎之參——參與、冒險、追求刺激',
      '井': '南方朱雀——滋潤、服務、樂於付出',
      '鬼': '朱雀之鬼——神秘、直覺、難以捉摸',
      '柳': '朱雀之柳——柔軟、適應、隨風擺動',
      '星': '朱雀之星——光亮、舞台、需要被看見',
      '張': '朱雀之張——擴張、張揚、追求卓越',
      '翼': '朱雀之翼——輔助、配合、善於協調',
      '軫': '朱雀之軫——車尾、收尾、承擔結果',
    };
    return hints[xx] ?? '獨特的星宿能量';
  }

  // ---------- Premium teaser: designed to create desire ----------

  Widget _buildPremiumTeaser(BasicChart chart) {
    final dayMaster = chart.bazi['day_master'] ?? '';
    final sunSign = chart.astrology['太陽']?['sign'] ?? '';
    final hdType = chart.humandesign['energy_type'] ?? '';
    final xingxiu = chart.xingxiu;

    // Build a preview sentence based on free data
    final previewText = _buildPreviewSentence(dayMaster, sunSign, hdType, xingxiu);

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
                    '整合畫像預覽',
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
                previewText,
                style: const TextStyle(fontSize: 15, height: 1.6),
              ),
              const SizedBox(height: 8),
              // Gradient fade to suggest more content
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
                '完整報告還包含',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber.shade900,
                ),
              ),
              const SizedBox(height: 12),
              _buildLockedItem(
                icon: Icons.person_outline,
                title: '五系統整合畫像',
                desc: '為什麼你同時是$dayMaster的剛毅、$sunSign的靈活、$hdType的獨特',
              ),
              _buildLockedItem(
                icon: Icons.balance,
                title: '優缺點立體分析',
                desc: '外在表現 / 內在需求 / 思維模式 / 行動策略 / 關係模式',
              ),
              _buildLockedItem(
                icon: Icons.lightbulb_outline,
                title: '人生課題',
                desc: '這輩子要學的核心功課——不是「更努力」，是「允許自己」',
              ),
              _buildLockedItem(
                icon: Icons.local_pharmacy_outlined,
                title: '生活處方籤',
                desc: '根據$dayMaster、$sunSign、$xingxiu宿量身打造的日常建議',
              ),
              _buildLockedItem(
                icon: Icons.picture_as_pdf_outlined,
                title: 'PDF 下載珍藏',
                desc: '把完整的你存下來，隨時回看',
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadingPremium ? null : _unlockFullReport,
                icon: _loadingPremium
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.lock_open),
                label: Text(_loadingPremium ? '生成中...' : '看看完整的你'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF667EEA),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
              const SizedBox(height: 10),
              // Q&A button
              OutlinedButton.icon(
                onPressed: () {
                  if (_basicChart != null) {
                    final chartJson = {
                      'bazi': _basicChart!.bazi,
                      'astrology': _basicChart!.astrology,
                      'ziwei': _basicChart!.ziwei,
                      'humandesign': _basicChart!.humandesign,
                      'xingxiu': _basicChart!.xingxiu,
                    };
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => AskScreen(chart: chartJson),
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.chat_bubble_outline, size: 18),
                label: const Text('向 AI 命理師提問'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF667EEA),
                  side: const BorderSide(color: Color(0xFF667EEA)),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _buildPreviewSentence(String dm, String sun, String hd, String xx) {
    // Generate a compelling preview that makes user want to read more
    final fragments = <String>[];
    if (dm.isNotEmpty) fragments.add('$dm日主的剛毅');
    if (sun.isNotEmpty) fragments.add('$sun的靈活多變');
    if (hd.isNotEmpty) fragments.add('$hd的獨特能量');
    if (xx.isNotEmpty) fragments.add('$xx宿的保護本能');

    if (fragments.length >= 2) {
      return '你是${fragments.join('、')}的組合。這些特質看似矛盾，卻在同一個人身上共存——這就是為什麼有時候連你自己都搞不清楚自己到底是誰。完整報告會告訴你，這些矛盾如何形成你獨一無二的形狀...';
    }
    return '你的命盤揭示了多個系統交織的獨特組合。這些特質看似矛盾，卻在同一個人身上共存——完整報告會告訴你，這些矛盾如何形成你獨一無二的形狀...';
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

  Widget _buildFullReportSection() {
    final report = _fullReport!;
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
                  Icon(Icons.auto_awesome, color: Colors.white),
                  SizedBox(width: 8),
                  Text(
                    '整合畫像',
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
                report.integratedProfile,
                style: const TextStyle(fontSize: 15, color: Colors.white, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          '優缺點分析',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...report.strengthsWeaknesses.entries.map((e) {
          final data = e.value as Map<String, dynamic>;
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              title: Text(e.key, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('✅ ${data['優點'] ?? data['strength'] ?? ''}', style: const TextStyle(color: Colors.green)),
                  Text('⚠️ ${data['缺點'] ?? data['weakness'] ?? ''}', style: const TextStyle(color: Colors.orange)),
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.indigo.shade50,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '人生課題',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(report.lifeLessons, style: const TextStyle(height: 1.6)),
            ],
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          '生活處方籤',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...report.prescription.map((p) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Text(p['icon'] ?? '💊', style: const TextStyle(fontSize: 24)),
            title: Text(p['title'] ?? ''),
            subtitle: Text(p['description'] ?? ''),
          ),
        )),
      ],
    );
  }

  // ---------- Detail tabs ----------

  Widget _buildBaziTab(BasicChart chart) {
    final bz = chart.bazi;
    final interp = chart.interpretations['bazi'] ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Free: only one interpretation fragment
          if (interp['day_master_trait'] != null)
            _buildTabInterpretation(
              title: '日主特質',
              content: interp['day_master_trait'],
              color: Colors.blue,
            ),
          // Locked preview for deeper analysis
          _buildLockedTabPreview(
            title: '五行能量調性',
            desc: '你的五行比例揭示了內在能量運作模式——什麼在推動你、什麼在消耗你',
            color: Colors.blue,
          ),
          _buildLockedTabPreview(
            title: '大運與流年趨勢',
            desc: '當前運勢階段與未來轉折點提示',
            color: Colors.blue,
          ),
          const Divider(height: 32),
          const Text('四柱資料', style: TextStyle(color: Colors.white54, fontSize: 12)),
          const SizedBox(height: 8),
          _buildInfoCard('年柱', bz['year'] ?? '-'),
          _buildInfoCard('月柱', bz['month'] ?? '-'),
          _buildInfoCard('日柱', bz['day'] ?? '-'),
          _buildInfoCard('時柱', bz['hour'] ?? '-'),
          _buildInfoCard('日主', bz['day_master'] ?? '-'),
        ],
      ),
    );
  }

  Widget _buildAstroTab(BasicChart chart) {
    final astro = chart.astrology;
    final interp = chart.interpretations['astrology'] ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Free: only sun sign trait
          if (interp['sun_sign_trait'] != null)
            _buildTabInterpretation(
              title: '太陽星座特質',
              content: interp['sun_sign_trait'],
              color: Colors.orange,
            ),
          // Locked previews
          _buildLockedTabPreview(
            title: '月亮星座的內在需求',
            desc: '你的情感模式與安全感來源——太陽是「你是誰」，月亮是「你需要什麼」',
            color: Colors.orange,
          ),
          _buildLockedTabPreview(
            title: '上升星座的外在面具',
            desc: '別人第一眼看到的你，與真實自我的落差',
            color: Colors.orange,
          ),
          const Divider(height: 32),
          const Text('行星位置', style: TextStyle(color: Colors.white54, fontSize: 12)),
          const SizedBox(height: 8),
          ...astro.entries.map((e) {
            final data = e.value as Map<String, dynamic>;
            return _buildInfoCard(
              e.key,
              '${data['sign']} ${data['degree']}°',
            );
          }),
        ],
      ),
    );
  }

  Widget _buildZiweiTab(BasicChart chart) {
    final zw = chart.ziwei;
    final interp = chart.interpretations['ziwei'] ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Free: only main star trait
          if (interp['main_star_trait'] != null)
            _buildTabInterpretation(
              title: '命宮主星特質',
              content: interp['main_star_trait'],
              color: Colors.red,
            ),
          // Locked previews
          _buildLockedTabPreview(
            title: '命宮格局與人生劇本',
            desc: '你的命宮結構揭示了這輩子的核心劇本——什麼在驅動你、什麼在限制你',
            color: Colors.red,
          ),
          _buildLockedTabPreview(
            title: '輔星與四化影響',
            desc: '祿、權、科、忌如何塑造你的際遇與選擇',
            color: Colors.red,
          ),
          const Divider(height: 32),
          const Text('命盤資料', style: TextStyle(color: Colors.white54, fontSize: 12)),
          const SizedBox(height: 8),
          _buildInfoCard('命宮', zw['命宮'] ?? '-'),
          _buildInfoCard('身宮', zw['身宮'] ?? '-'),
          _buildInfoCard('五行局', zw['五行局'] ?? '-'),
          _buildInfoCard('紫微', zw['紫微'] ?? '-'),
          _buildInfoCard('天府', zw['天府'] ?? '-'),
        ],
      ),
    );
  }

  Widget _buildHDTab(BasicChart chart) {
    final hd = chart.humandesign;
    final interp = chart.interpretations['humandesign'] ?? {};
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Free: only energy type trait
          if (interp['type_trait'] != null)
            _buildTabInterpretation(
              title: '能量類型特質',
              content: interp['type_trait'],
              color: Colors.purple,
            ),
          // Locked previews
          _buildLockedTabPreview(
            title: '人生策略',
            desc: '你的能量類型決定了正確的人生策略——做對了事半功倍，做錯了事倍功半',
            color: Colors.purple,
          ),
          _buildLockedTabPreview(
            title: '內在權威與決策方式',
            desc: '你的身體如何替你做出正確決定——不是頭腦，而是內在權威',
            color: Colors.purple,
          ),
          _buildLockedTabPreview(
            title: '人生角色與輪迴交叉',
            desc: '你來這一世要扮演的角色，以及靈魂的更深層使命',
            color: Colors.purple,
          ),
          const Divider(height: 32),
          const Text('人類圖資料', style: TextStyle(color: Colors.white54, fontSize: 12)),
          const SizedBox(height: 8),
          _buildInfoCard('能量類型', hd['energy_type'] ?? '-'),
          _buildInfoCard('人生角色', hd['profile'] ?? '-'),
          _buildInfoCard('內在權威', hd['authority'] ?? '-'),
          _buildInfoCard(
            '定義中心',
            (hd['defined_centers'] as List<dynamic>?)?.join('、') ?? '-',
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(String title, String value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: const Color(0xFF1E1E2E),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        title: Text(title, style: const TextStyle(color: Colors.white54, fontSize: 14)),
        subtitle: Text(
          value,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
        ),
      ),
    );
  }

  Widget _buildTabInterpretation({
    required String title,
    required dynamic content,
    required MaterialColor color,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.shade900.withAlpha(60), color.shade900.withAlpha(20)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.shade700.withAlpha(80)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 4,
                height: 16,
                decoration: BoxDecoration(
                  color: color.shade400,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                title,
                style: TextStyle(
                  color: color.shade300,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            content.toString(),
            style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.7),
          ),
        ],
      ),
    );
  }

  Widget _buildLockedTabPreview({
    required String title,
    required String desc,
    required MaterialColor color,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900.withAlpha(60),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade800),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.lock_outline, size: 18, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: Colors.grey.shade500,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  desc,
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 12,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
