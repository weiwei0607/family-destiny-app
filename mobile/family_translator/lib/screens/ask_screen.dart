import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AskScreen extends StatefulWidget {
  final Map<String, dynamic> chart;

  const AskScreen({super.key, required this.chart});

  @override
  State<AskScreen> createState() => _AskScreenState();
}

class _AskScreenState extends State<AskScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<_QAMessage> _messages = [];
  bool _isLoading = false;

  final List<String> _quickQuestions = [
    '我適合做什麼類型的工作？',
    '現在適合談戀愛嗎？',
    '我該不該換工作？',
    '我在人際關係中要注意什麼？',
    '我的健康需要注意什麼？',
  ];

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _sendQuestion(String question) async {
    if (question.trim().isEmpty) return;

    setState(() {
      _messages.add(_QAMessage(
        text: question.trim(),
        isUser: true,
      ));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await ApiService().askQuestion(
        chart: widget.chart,
        question: question.trim(),
        tier: 'standard',
      );

      setState(() {
        _messages.add(_QAMessage(
          text: response.answer,
          isUser: false,
          relevantSystems: response.relevantSystems,
          confidence: response.confidence,
          disclaimer: response.disclaimer,
        ));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(_QAMessage(
          text: '抱歉，暫時無法回答這個問題。請稍後再試。',
          isUser: false,
          isError: true,
        ));
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0F1A),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          '向 AI 提問',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      return _buildMessageBubble(_messages[index]);
                    },
                  ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.amber),
                    ),
                  ),
                  SizedBox(width: 8),
                  Text(
                    'AI 正在結合你的命盤思考中...',
                    style: TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                ],
              ),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
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
                  '💡 你可以這樣問',
                  style: TextStyle(
                    color: Colors.amber,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'AI 會結合你的八字、占星、紫微、人類圖、星宿五個系統來回答。問題越具體，回答越精準。',
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            '熱門問題',
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _quickQuestions.map((q) {
              return ActionChip(
                backgroundColor: const Color(0xFF1E1E2E),
                side: const BorderSide(color: Colors.white12),
                label: Text(
                  q,
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
                onPressed: () => _sendQuestion(q),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(_QAMessage msg) {
    if (msg.isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(left: 40, bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF6C5DD3), Color(0xFF8B5CF6)],
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            msg.text,
            style: const TextStyle(color: Colors.white, fontSize: 15),
          ),
        ),
      );
    }

    // AI message
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(right: 16, bottom: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // AI avatar + name
            Row(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.auto_awesome, size: 14, color: Colors.white),
                ),
                const SizedBox(width: 8),
                const Text(
                  'AI 命理師',
                  style: TextStyle(
                    color: Colors.amber,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Answer bubble
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
                  Text(
                    msg.text,
                    style: TextStyle(
                      color: msg.isError ? Colors.red[300] : Colors.white,
                      fontSize: 15,
                      height: 1.6,
                    ),
                  ),
                  if (!msg.isError && msg.relevantSystems != null) ...[
                    const SizedBox(height: 16),
                    _buildMetaRow('參考系統', msg.relevantSystems!.join(' · ')),
                    const SizedBox(height: 6),
                    _buildMetaRow('信心程度', msg.confidence ?? '中'),
                  ],
                  if (!msg.isError && msg.disclaimer != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.amber.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.amber.withOpacity(0.2)),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.info_outline, size: 14, color: Colors.amber[300]),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              msg.disclaimer!,
                              style: TextStyle(
                                color: Colors.amber[200],
                                fontSize: 11,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetaRow(String label, String value) {
    return Row(
      children: [
        Text(
          '$label：',
          style: TextStyle(color: Colors.white.withAlpha(102), fontSize: 12),
        ),
        Text(
          value,
          style: const TextStyle(color: Colors.white60, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F1A),
        border: Border(top: BorderSide(color: Colors.white.withOpacity(0.08))),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                style: const TextStyle(color: Colors.white, fontSize: 15),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: (value) => _sendQuestion(value),
                decoration: InputDecoration(
                  hintText: '輸入你的問題...',
                  hintStyle: TextStyle(color: Colors.white.withOpacity(0.3)),
                  filled: true,
                  fillColor: const Color(0xFF1E1E2E),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: () => _sendQuestion(_controller.text),
              child: Container(
                width: 48,
                height: 48,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
                  ),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.send, color: Colors.white, size: 20),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _QAMessage {
  final String text;
  final bool isUser;
  final bool isError;
  final List<String>? relevantSystems;
  final String? confidence;
  final String? disclaimer;

  _QAMessage({
    required this.text,
    required this.isUser,
    this.isError = false,
    this.relevantSystems,
    this.confidence,
    this.disclaimer,
  });
}
