from typing import Dict, List, Optional, Union
import openai
from app.core.config import get_settings
import logging
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class GradingService:
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.OPENAI_API_KEY

    async def grade_submission(self, 
                             content: str, 
                             rubric: Dict,
                             submission_type: str = "text",
                             max_score: float = 100.0) -> Dict:
        """
        Grade a submission using AI based on a provided rubric.
        
        Args:
            content: The content to grade
            rubric: Dictionary containing grading criteria and weights
            submission_type: Type of submission (text, code, essay, etc.)
            max_score: Maximum possible score
            
        Returns:
            Dict containing grading results and feedback
        """
        try:
            # Prepare the grading prompt
            prompt = self._create_grading_prompt(content, rubric, submission_type, max_score)
            
            # Get AI evaluation
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert grader. Provide detailed, constructive feedback and accurate scoring based on the given rubric."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the response
            evaluation = json.loads(response.choices[0].message.content)
            
            # Add metadata
            evaluation.update({
                "submission_type": submission_type,
                "max_score": max_score,
                "graded_at": datetime.utcnow().isoformat(),
                "model_used": "gpt-4"
            })
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in grading submission: {str(e)}")
            raise

    async def grade_code_submission(self, 
                                  code: str, 
                                  requirements: List[str],
                                  test_cases: Optional[List[Dict]] = None) -> Dict:
        """
        Grade a code submission with specific focus on code quality and functionality.
        
        Args:
            code: The code to grade
            requirements: List of requirements the code should meet
            test_cases: Optional list of test cases to evaluate
            
        Returns:
            Dict containing code evaluation results
        """
        try:
            # Prepare code-specific grading prompt
            prompt = self._create_code_grading_prompt(code, requirements, test_cases)
            
            # Get AI evaluation
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Evaluate code quality, functionality, and adherence to requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the response
            evaluation = json.loads(response.choices[0].message.content)
            
            # Add metadata
            evaluation.update({
                "submission_type": "code",
                "graded_at": datetime.utcnow().isoformat(),
                "model_used": "gpt-4"
            })
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in grading code submission: {str(e)}")
            raise

    async def grade_essay(self, 
                         essay: str, 
                         rubric: Dict,
                         word_count: Optional[int] = None) -> Dict:
        """
        Grade an essay with focus on content, structure, and writing quality.
        
        Args:
            essay: The essay text to grade
            rubric: Dictionary containing essay grading criteria
            word_count: Optional target word count
            
        Returns:
            Dict containing essay evaluation results
        """
        try:
            # Prepare essay-specific grading prompt
            prompt = self._create_essay_grading_prompt(essay, rubric, word_count)
            
            # Get AI evaluation
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert essay grader. Evaluate writing quality, argumentation, and adherence to requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the response
            evaluation = json.loads(response.choices[0].message.content)
            
            # Add metadata
            evaluation.update({
                "submission_type": "essay",
                "graded_at": datetime.utcnow().isoformat(),
                "model_used": "gpt-4"
            })
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in grading essay: {str(e)}")
            raise

    def _create_grading_prompt(self, content: str, rubric: Dict, 
                             submission_type: str, max_score: float) -> str:
        """Create a prompt for general grading."""
        prompt = f"""
        Please grade the following {submission_type} submission according to the rubric.
        Maximum possible score: {max_score}
        
        Rubric:
        {json.dumps(rubric, indent=2)}
        
        Submission:
        {content}
        
        Please provide a JSON response with the following structure:
        {{
            "score": float,
            "feedback": {{
                "overall": str,
                "criterion_specific": Dict[str, str],
                "strengths": List[str],
                "areas_for_improvement": List[str]
            }},
            "detailed_analysis": Dict[str, float]
        }}
        """
        return prompt

    def _create_code_grading_prompt(self, code: str, requirements: List[str], 
                                  test_cases: Optional[List[Dict]]) -> str:
        """Create a prompt for code grading."""
        prompt = f"""
        Please evaluate the following code submission according to the requirements.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Code:
        {code}
        
        {f'Test Cases:\n{json.dumps(test_cases, indent=2)}' if test_cases else ''}
        
        Please provide a JSON response with the following structure:
        {{
            "score": float,
            "feedback": {{
                "overall": str,
                "code_quality": str,
                "functionality": str,
                "requirements_met": List[str],
                "requirements_missed": List[str],
                "suggestions": List[str]
            }},
            "detailed_analysis": {{
                "code_style": float,
                "efficiency": float,
                "documentation": float,
                "functionality": float
            }}
        }}
        """
        return prompt

    def _create_essay_grading_prompt(self, essay: str, rubric: Dict, 
                                   word_count: Optional[int]) -> str:
        """Create a prompt for essay grading."""
        prompt = f"""
        Please grade the following essay according to the rubric.
        
        Rubric:
        {json.dumps(rubric, indent=2)}
        
        {f'Target word count: {word_count}' if word_count else ''}
        
        Essay:
        {essay}
        
        Please provide a JSON response with the following structure:
        {{
            "score": float,
            "feedback": {{
                "overall": str,
                "content": str,
                "structure": str,
                "writing_quality": str,
                "strengths": List[str],
                "areas_for_improvement": List[str]
            }},
            "detailed_analysis": {{
                "content": float,
                "organization": float,
                "language": float,
                "mechanics": float
            }}
        }}
        """
        return prompt

    async def batch_grade(self, submissions: List[Dict]) -> List[Dict]:
        """
        Grade multiple submissions in parallel.
        
        Args:
            submissions: List of submission dictionaries containing content and grading parameters
            
        Returns:
            List of grading results
        """
        try:
            tasks = []
            for submission in submissions:
                if submission["type"] == "code":
                    task = self.grade_code_submission(
                        submission["content"],
                        submission["requirements"],
                        submission.get("test_cases")
                    )
                elif submission["type"] == "essay":
                    task = self.grade_essay(
                        submission["content"],
                        submission["rubric"],
                        submission.get("word_count")
                    )
                else:
                    task = self.grade_submission(
                        submission["content"],
                        submission["rubric"],
                        submission["type"],
                        submission.get("max_score", 100.0)
                    )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
            
        except Exception as e:
            logger.error(f"Error in batch grading: {str(e)}")
            raise 
