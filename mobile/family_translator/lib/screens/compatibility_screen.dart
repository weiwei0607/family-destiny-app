import 'package:flutter/material.dart';
import 'compatibility_report_screen.dart';

class CompatibilityScreen extends StatefulWidget {
  const CompatibilityScreen({super.key});

  @override
  State<CompatibilityScreen> createState() => _CompatibilityScreenState();
}

class _CompatibilityScreenState extends State<CompatibilityScreen> {
  final _name1Ctrl = TextEditingController();
  final _name2Ctrl = TextEditingController();
  String _gender1 = '女';
  String _gender2 = '男';
  DateTime? _date1;
  DateTime? _date2;
  TimeOfDay _time1 = const TimeOfDay(hour: 12, minute: 0);
  TimeOfDay _time2 = const TimeOfDay(hour: 12, minute: 0);

  Future<void> _pickDate(int person) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(1999, 6, 7),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        if (person == 1) _date1 = picked;
        else _date2 = picked;
      });
    }
  }

  Future<void> _pickTime(int person) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: person == 1 ? _time1 : _time2,
    );
    if (picked != null) {
      setState(() {
        if (person == 1) _time1 = picked;
        else _time2 = picked;
      });
    }
  }

  void _submit() {
    if (_date1 == null || _date2 == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('請選擇雙方的出生日期')),
      );
      return;
    }

    final person1 = {
      'name': _name1Ctrl.text,
      'gender': _gender1,
      'date': '${_date1!.year}-${_date1!.month.toString().padLeft(2, '0')}-${_date1!.day.toString().padLeft(2, '0')}',
      'time': '${_time1.hour.toString().padLeft(2, '0')}:${_time1.minute.toString().padLeft(2, '0')}',
      'location': 'taipei',
    };

    final person2 = {
      'name': _name2Ctrl.text,
      'gender': _gender2,
      'date': '${_date2!.year}-${_date2!.month.toString().padLeft(2, '0')}-${_date2!.day.toString().padLeft(2, '0')}',
      'time': '${_time2.hour.toString().padLeft(2, '0')}:${_time2.minute.toString().padLeft(2, '0')}',
      'location': 'taipei',
    };

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CompatibilityReportScreen(
          person1: person1,
          person2: person2,
        ),
      ),
    );
  }

  Widget _buildPersonForm(int person) {
    final isPerson1 = person == 1;
    final nameCtrl = isPerson1 ? _name1Ctrl : _name2Ctrl;
    final gender = isPerson1 ? _gender1 : _gender2;
    final date = isPerson1 ? _date1 : _date2;
    final time = isPerson1 ? _time1 : _time2;
    final color = isPerson1 ? const Color(0xFF667EEA) : const Color(0xFFE91E63);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isPerson1 ? '👤 你' : '💕 對方',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: nameCtrl,
          decoration: InputDecoration(
            labelText: '姓名',
            hintText: isPerson1 ? '例如：韡寧' : '例如：男友',
            border: const OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          value: gender,
          decoration: const InputDecoration(
            labelText: '性別',
            border: OutlineInputBorder(),
          ),
          items: const [
            DropdownMenuItem(value: '女', child: Text('女')),
            DropdownMenuItem(value: '男', child: Text('男')),
          ],
          onChanged: (v) => setState(() {
            if (isPerson1) _gender1 = v!;
            else _gender2 = v!;
          }),
        ),
        const SizedBox(height: 12),
        InkWell(
          onTap: () => _pickDate(person),
          child: InputDecorator(
            decoration: const InputDecoration(
              labelText: '出生日期 *',
              border: OutlineInputBorder(),
            ),
            child: Text(
              date == null ? '請選擇日期' : '${date.year}/${date.month}/${date.day}',
            ),
          ),
        ),
        const SizedBox(height: 12),
        InkWell(
          onTap: () => _pickTime(person),
          child: InputDecorator(
            decoration: const InputDecoration(
              labelText: '出生時間',
              border: OutlineInputBorder(),
            ),
            child: Text(
              '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}',
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('💕 戀愛合盤'),
        backgroundColor: const Color(0xFF667EEA),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              '輸入兩個人的資料，看你們合不合',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(child: _buildPersonForm(1)),
                const SizedBox(width: 16),
                Expanded(child: _buildPersonForm(2)),
              ],
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: _submit,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF667EEA),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                '💕 開始合盤分析',
                style: TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
