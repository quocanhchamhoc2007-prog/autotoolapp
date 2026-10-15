import logging

logger = logging.getLogger(__name__)

class ContentQualityChecker:
    @staticmethod
    def evaluate_post(content: str, target_words: int = 800) -> dict:
        """
        Kiểm tra chất lượng bài viết dựa trên số từ, số đoạn văn và cấu trúc.
        """
        if not content:
            return {"is_valid": False, "score": 0, "error": "Nội dung bài viết trống."}

        words = content.split()
        actual_word_count = len(words)
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs)

        score = 100
        issues = []

        # Kiểm tra độ dài so với mục tiêu
        if actual_word_count < target_words * 0.7:
            score -= 30
            issues.append(f"Bài viết quá ngắn ({actual_word_count}/{target_words} từ mục tiêu).")

        # Kiểm tra cấu trúc đoạn văn
        if paragraph_count < 4:
            score -= 20
            issues.append("Số lượng đoạn văn quá ít, thiếu chiều sâu triển khai.")

        is_valid = score >= 70
        return {
            "is_valid": is_valid,
            "score": max(0, score),
            "actual_word_count": actual_word_count,
            "paragraph_count": paragraph_count,
            "issues": issues
        }