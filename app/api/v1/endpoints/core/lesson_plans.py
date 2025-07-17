from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.educational.curriculum.lesson_plan import LessonPlan
from app.schemas.lesson_plan import LessonPlanSchema
from app.services.document_service import get_document_service, DocumentService
from app.services.ai.ai_lesson_enhancement import get_ai_enhancement_service, AILessonEnhancement
from app.examples.example_lesson_plans import get_pe_lesson_plan, get_health_lesson_plan, get_drivers_ed_lesson_plan
from pydantic import BaseModel

router = APIRouter()

class VirtualAssistantQuery(BaseModel):
    """Schema for virtual assistant queries."""
    lesson_plan: LessonPlanSchema
    query: str

@router.post("/lesson-plans/enhance", response_model=Dict[str, Any])
async def enhance_lesson_plan(
    lesson_plan: LessonPlanSchema,
    ai_service: AILessonEnhancement = Depends(get_ai_enhancement_service),
    doc_service: DocumentService = Depends(get_document_service)
) -> Dict[str, Any]:
    """
    Enhance a lesson plan with AI-generated content and resources.
    
    This endpoint:
    1. Generates personalized content
    2. Enhances differentiation strategies
    3. Creates multimedia resources
    4. Develops assessment tools
    5. Provides language support
    6. Creates a virtual teaching assistant
    7. Generates the final document
    """
    try:
        # Convert Pydantic model to SQLAlchemy model
        db_lesson_plan = LessonPlan(**lesson_plan.model_dump())
        
        # Get AI enhancements
        enhancements = await ai_service.enhance_lesson_plan(db_lesson_plan)
        
        # Create virtual assistant
        assistant = await ai_service.generate_virtual_assistant(db_lesson_plan)
        
        # Generate document
        doc_path = await doc_service.generate_lesson_plan(db_lesson_plan)
        
        return {
            "enhancements": enhancements,
            "virtual_assistant": assistant,
            "document_path": doc_path,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lesson-plans/examples/{subject}", response_model=Dict[str, Any])
async def get_example_lesson_plan(
    subject: str,
    ai_service: AILessonEnhancement = Depends(get_ai_enhancement_service)
) -> Dict[str, Any]:
    """Get an AI-enhanced example lesson plan for a specific subject."""
    try:
        # Get base lesson plan
        if subject.lower() == "pe":
            lesson_plan = get_pe_lesson_plan()
        elif subject.lower() == "health":
            lesson_plan = get_health_lesson_plan()
        elif subject.lower() == "drivers-ed":
            lesson_plan = get_drivers_ed_lesson_plan()
        else:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Convert to Pydantic model
        lesson_plan_schema = LessonPlanSchema.model_validate(lesson_plan)
        
        # Enhance with AI
        enhancements = await ai_service.enhance_lesson_plan(lesson_plan)
        
        return {
            "lesson_plan": lesson_plan_schema.model_dump(),
            "ai_enhancements": enhancements,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lesson-plans/virtual-assistant/query", response_model=Dict[str, Any])
async def query_virtual_assistant(
    request: VirtualAssistantQuery,
    ai_service: AILessonEnhancement = Depends(get_ai_enhancement_service)
) -> Dict[str, Any]:
    """Query the virtual teaching assistant for a specific lesson plan."""
    try:
        # Convert Pydantic model to SQLAlchemy model
        lesson_plan = LessonPlan(**request.lesson_plan.model_dump())
        
        # Create context-aware prompt
        prompt = f"""
        As a virtual teaching assistant for {lesson_plan.lesson_title}, 
        please answer the following question:
        {request.query}
        
        Consider:
        - Grade Level: {lesson_plan.grade_level}
        - Subject: {lesson_plan.subject}
        - Learning Objectives: {lesson_plan.objectives}
        """
        
        response = await ai_service.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and patient teaching assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return {
            "response": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 