import os
import uuid
import random
import string
import json
import numpy as np
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# Configuration & AI Setup
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. AI features will fail.")

app = FastAPI(title="C&S Think tank API")

# ==========================================
# Data Models
# ==========================================
class CommentBase(BaseModel):
    author: str
    text: str
    parentId: Optional[str] = None
    upvotes: int = 0
    attachment: Optional[str] = None  # Base64 data URL

class Comment(CommentBase):
    id: str
    timestamp: str

class IdeaBase(BaseModel):
    title: str
    description: str
    category: str
    author: str
    tagged_employees: List[str] = []
    attachment: Optional[str] = None # Base64 data URL

class Idea(IdeaBase):
    id: str
    status: str = "Proposed"
    upvotes: int = 0
    comments: List[Comment] = []
    summary: Optional[str] = None
    embedding: Optional[List[float]] = None

class NewsletterBase(BaseModel):
    title: str
    content: str
    author: str
    attachment: Optional[str] = None

class Newsletter(NewsletterBase):
    id: str
    timestamp: str

# ==========================================
# Persistent Storage System
# ==========================================
db_ideas: Dict[str, Idea] = {}
db_newsletters: Dict[str, Newsletter] = {}
STORAGE_FILE = "storage.json"

def get_embedding(text: str) -> List[float]:
    if not client: return [0.0] * 768 
    try:
        # Try the newest embedding model
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        # Fallback to the universally available model if 004 is restricted on this API key
        try:
            response = client.models.embed_content(
                model="embedding-001",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as fallback_e:
            print(f"Warning: Failed to generate embedding: {fallback_e}")
            return [0.0] * 768

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0: return 0.0
    return float(dot_product / (norm_a * norm_b))

def generate_id(prefix="IDEA"):
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{chars}"

def save_data():
    """Saves the current state to a JSON file to persist across restarts."""
    with open(STORAGE_FILE, "w") as f:
        json.dump({
            "ideas": {k: v.dict() for k, v in db_ideas.items()},
            "newsletters": {k: v.dict() for k, v in db_newsletters.items()}
        }, f)

def load_data():
    """Loads state from JSON, or seeds it if it doesn't exist."""
    global db_ideas, db_newsletters
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)
            db_ideas = {k: Idea(**v) for k, v in data.get("ideas", {}).items()}
            db_newsletters = {k: Newsletter(**v) for k, v in data.get("newsletters", {}).items()}
    else:
        seed_data()
        save_data()

def seed_data():
    """Injects initial mock data if starting fresh."""
    mock_ideas = [
        {
            "id": "IDEA-A7F2", "title": "Automate Weekly KPI Reports", "description": "Currently we spend 3 hours manually pulling data from 4 systems. We should write a Python script to aggregate this automatically.", "category": "Process Improvement", "author": "Alice Eng", "tagged_employees": ["Bob Data", "Charlie Ops"], "status": "Proposed", "upvotes": 12,
            "comments": [
                Comment(id="c1", author="Bob Data", text="I can provide the API keys for the data warehouse.", timestamp="2 days ago", parentId=None, upvotes=5),
                Comment(id="c2", author="Charlie Ops", text="Great idea. Let's schedule a kickoff next Tuesday.", timestamp="1 day ago", parentId=None, upvotes=2),
                Comment(id="c3", author="Alice Eng", text="Thanks Charlie, I'll send out the invite shortly.", timestamp="1 day ago", parentId="c2", upvotes=1),
                Comment(id="c4", author="Dave IT", text="Will this connect to the new ERP system?", timestamp="5 hours ago", parentId=None, upvotes=3)
            ]
        },
        {
            "id": "IDEA-B8X9", "title": "New Warehouse Onboarding Portal", "description": "Staff are getting confused with our current PDF guides. Let's build a simple web portal for them to track their onboarding progress.", "category": "New Idea", "author": "Sarah Operations", "tagged_employees": ["Alex Dev"], "status": "Under Review", "upvotes": 18,
            "comments": [
                Comment(id="c5", author="Mike Supervisor", text="We definitely need this, PDFs are outdated.", timestamp="3 days ago", parentId=None, upvotes=8),
                Comment(id="c6", author="Sarah Operations", text="I have some wireframes we could use as a starting point.", timestamp="2 days ago", parentId=None, upvotes=4),
                Comment(id="c7", author="Alex Dev", text="Send them over, we can build a prototype by next sprint.", timestamp="1 day ago", parentId="c6", upvotes=5),
                Comment(id="c8", author="Maria HR", text="Ensure it complies with the latest safety training modules.", timestamp="12 hours ago", parentId=None, upvotes=7)
            ]
        },
        {
            "id": "IDEA-X912", "title": "Optimize Forklift Routing", "description": "We can reduce transit time by 15% if we implement a one-way pathing system in the heavy storage aisles.", "category": "Process Improvement", "author": "James Warehouse", "tagged_employees": [], "status": "Proposed", "upvotes": 24,
            "comments": [
                Comment(id="c9", author="Tom Manager", text="We tried this in 2019 but ran into bottleneck issues near loading dock B.", timestamp="4 days ago", parentId=None, upvotes=6),
                Comment(id="c10", author="James Warehouse", text="Good point. We expanded Dock B since then, so the clearance is much wider now.", timestamp="3 days ago", parentId="c9", upvotes=4),
                Comment(id="c11", author="Tom Manager", text="Ah, true. Let's pilot this in Aisle 4 next week.", timestamp="2 days ago", parentId="c10", upvotes=5)
            ]
        },
        {
            "id": "IDEA-S4W1", "title": "Switch to Biodegradable Shrink Wrap", "description": "We use miles of plastic wrap daily. Switching to a biodegradable alternative would drastically reduce our carbon footprint and align with our sustainability goals.", "category": "Process Improvement", "author": "Eco Team", "tagged_employees": ["Kevin Finance"], "status": "Under Review", "upvotes": 45,
            "comments": [
                Comment(id="c12", author="Eco Team", text="I've contacted 3 vendors for bulk pricing.", timestamp="1 week ago", parentId=None, upvotes=12),
                Comment(id="c13", author="Kevin Finance", text="What is the estimated cost difference per pallet?", timestamp="5 days ago", parentId=None, upvotes=2),
                Comment(id="c14", author="Eco Team", text="About 4% more upfront, but largely offset by our waste disposal savings.", timestamp="4 days ago", parentId="c13", upvotes=9),
                Comment(id="c15", author="CEO Office", text="Love this. Let's review the final numbers on Friday.", timestamp="1 day ago", parentId=None, upvotes=15)
            ]
        },
        {
            "id": "IDEA-V7P3", "title": "Implement Voice Picking Tech", "description": "Warehouse selectors could move much faster if we upgraded to voice-directed picking headsets rather than using handheld scanners. Keeps hands free.", "category": "Process Improvement", "author": "John Logistics", "tagged_employees": [], "status": "Proposed", "upvotes": 30,
            "comments": [
                Comment(id="c16", author="John Logistics", text="Other DCs in our network saw a 20% speed increase with this.", timestamp="2 weeks ago", parentId=None, upvotes=8),
                Comment(id="c17", author="Tech Support", text="We need to check Wi-Fi coverage in the dead zones first.", timestamp="10 days ago", parentId=None, upvotes=5),
                Comment(id="c18", author="Network Admin", text="Access points are being upgraded next month, perfect timing.", timestamp="9 days ago", parentId="c17", upvotes=11)
            ]
        },
        {
            "id": "IDEA-M2C9", "title": "Quarterly Cross-Department Mixer", "description": "There are a lot of silos between procurement, sales, and operations. A casual quarterly mixer event would improve relations and cross-functional problem solving.", "category": "Culture & Team", "author": "HR Dept", "tagged_employees": [], "status": "Implemented", "upvotes": 55,
            "comments": [
                Comment(id="c19", author="HR Dept", text="Budget has been officially approved for Q2!", timestamp="1 month ago", parentId=None, upvotes=22),
                Comment(id="c20", author="Ops Lead", text="Can we do it on a Thursday afternoon? Fridays are tough for shipping.", timestamp="3 weeks ago", parentId=None, upvotes=14),
                Comment(id="c21", author="Sales Director", text="Thursday works best for the sales team as well.", timestamp="3 weeks ago", parentId="c20", upvotes=8)
            ]
        },
        {
            "id": "IDEA-L9E4", "title": "Solar Panels for Hatfield Facility", "description": "The roof of the Hatfield warehouse is massive and unobstructed. Installing solar panels could offset 30% of our energy costs over the next decade.", "category": "Process Improvement", "author": "Facilities Mgmt", "tagged_employees": ["Exec Team"], "status": "Under Review", "upvotes": 82,
            "comments": [
                Comment(id="c22", author="Facilities Mgmt", text="State green energy grants could cover up to 40% of the installation costs.", timestamp="2 months ago", parentId=None, upvotes=30),
                Comment(id="c23", author="Kevin Finance", text="Initial ROI is estimated at 4.5 years, which is excellent.", timestamp="1 month ago", parentId=None, upvotes=18),
                Comment(id="c24", author="Exec Team", text="Proceed to Phase 1 feasibility study. Great initiative.", timestamp="3 weeks ago", parentId=None, upvotes=45),
                Comment(id="c25", author="Facilities Mgmt", text="Consultants are coming in next week to survey the roof.", timestamp="2 weeks ago", parentId="c24", upvotes=12)
            ]
        },
        {
            "id": "IDEA-I3T8", "title": "Mobile App for Inventory Tracking", "description": "Floor managers need a quick mobile app on their company phones to scan and check inventory levels instantly, instead of walking back to a fixed terminal.", "category": "New Idea", "author": "IT Systems", "tagged_employees": [], "status": "Proposed", "upvotes": 41,
            "comments": [
                Comment(id="c26", author="Alex Dev", text="We can build this cross-platform using React Native.", timestamp="5 days ago", parentId=None, upvotes=10),
                Comment(id="c27", author="Floor Supervisor", text="It absolutely MUST have an offline mode for the freezer sections.", timestamp="4 days ago", parentId=None, upvotes=25),
                Comment(id="c28", author="Alex Dev", text="Noted. Local caching and sync-on-reconnect will be implemented.", timestamp="3 days ago", parentId="c27", upvotes=15),
                Comment(id="c29", author="IT Systems", text="I'll draft the architecture document this week.", timestamp="1 day ago", parentId=None, upvotes=7)
            ]
        }
    ]
    
    for idea_data in mock_ideas:
        iid = idea_data["id"]
        title = idea_data["title"]
        desc = idea_data["description"]
        cat = idea_data["category"]
        author = idea_data["author"]
        votes = idea_data["upvotes"]
        status = idea_data["status"]
        tagged = idea_data.get("tagged_employees", [])
        comments = idea_data.get("comments", [])
        
        db_ideas[iid] = Idea(
            id=iid, title=title, description=desc, category=cat, author=author, upvotes=votes, status=status, tagged_employees=tagged,
            embedding=get_embedding(f"{title}. {desc}") if client else [0.0]*768,
            comments=comments
        )

    news1 = generate_id("NEWS")
    db_newsletters[news1] = Newsletter(id=news1, title="Q3 Leadership Update", content="As we head into the busy holiday season, I want to thank everyone for their incredible dedication. Our supply chain resilience has never been stronger. Please review the updated holiday schedules.", author="Executive Team", timestamp="2 days ago")
    news2 = generate_id("NEWS")
    db_newsletters[news2] = Newsletter(id=news2, title="New Facility Opening in Midwest", content="We are thrilled to announce the ribbon-cutting of our newest distribution center next month. This 500,000 sq ft facility will support over 200 new grocery locations.", author="Operations PR", timestamp="1 week ago")
    news3 = generate_id("NEWS")
    db_newsletters[news3] = Newsletter(id=news3, title="Welcome to C&S Think tank!", content="This new platform is designed to give every employee a voice. Share your ideas, attach files, and let's build the future of food distribution together.", author="Innovation Team", timestamp="2 weeks ago")

# Load data on script start
load_data()

# ==========================================
# API Routes
# ==========================================
@app.get("/api/ideas", response_model=List[Idea])
async def get_ideas():
    return list(db_ideas.values())

@app.post("/api/ideas", response_model=Idea)
async def create_idea(idea_in: IdeaBase):
    new_id = generate_id("IDEA")
    embedding = get_embedding(f"{idea_in.title}. {idea_in.description}")
    new_idea = Idea(**idea_in.dict(), id=new_id, embedding=embedding)
    db_ideas[new_id] = new_idea
    save_data()
    return new_idea

@app.get("/api/ideas/{idea_id}", response_model=Idea)
async def get_idea(idea_id: str):
    if idea_id not in db_ideas: raise HTTPException(status_code=404)
    return db_ideas[idea_id]

@app.post("/api/ideas/{idea_id}/upvote")
async def upvote_idea(idea_id: str):
    if idea_id not in db_ideas: raise HTTPException(status_code=404)
    db_ideas[idea_id].upvotes += 1
    save_data()
    return {"status": "success", "upvotes": db_ideas[idea_id].upvotes}

@app.post("/api/ideas/{idea_id}/comments", response_model=Idea)
async def add_comment(idea_id: str, comment_in: CommentBase):
    if idea_id not in db_ideas: raise HTTPException(status_code=404)
    new_comment = Comment(**comment_in.dict(), id=str(uuid.uuid4()), timestamp="Just now")
    db_ideas[idea_id].comments.append(new_comment)
    save_data()
    return db_ideas[idea_id]

@app.post("/api/ideas/{idea_id}/comments/{comment_id}/vote")
async def vote_comment(idea_id: str, comment_id: str, delta: int):
    if idea_id not in db_ideas: raise HTTPException(status_code=404)
    for comment in db_ideas[idea_id].comments:
        if comment.id == comment_id:
            comment.upvotes += delta
            save_data()
            return {"status": "success", "upvotes": comment.upvotes}
    raise HTTPException(status_code=404)

@app.post("/api/ideas/{idea_id}/summarize")
async def summarize_idea(idea_id: str):
    if idea_id not in db_ideas: raise HTTPException(status_code=404)
    idea = db_ideas[idea_id]
    
    if not client:
        idea.summary = "API Key missing or invalid. Cannot generate AI summary."
        return {"summary": idea.summary}

    context = f"Idea Title: {idea.title}\nDescription: {idea.description}\n\nComments:\n"
    for c in idea.comments: context += f"- {c.author}: {c.text}\n"
    
    prompt = "You are an internal company assistant. Read the following idea and discussion thread. Provide a concise summary (max 3-4 sentences). Highlight key takeaways, action items, and the general sentiment.\n\n" + context

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        idea.summary = response.text
        idea.embedding = get_embedding(f"{idea.title}. {idea.description}. Summary: {idea.summary}")
        save_data()
        return {"summary": idea.summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search", response_model=List[Idea])
async def search_ideas(q: str):
    if not q: return list(db_ideas.values())
    q_upper = q.upper()
    if q_upper in db_ideas: return [db_ideas[q_upper]]

    query_embedding = get_embedding(q)
    results = []
    for idea in db_ideas.values():
        if idea.embedding:
            similarity = cosine_similarity(query_embedding, idea.embedding)
            results.append((similarity, idea))
            
    results.sort(key=lambda x: x[0], reverse=True)
    filtered = [res[1] for res in results if res[0] > 0.4] 
    
    if not filtered:
       for idea in db_ideas.values():
           if q.lower() in idea.title.lower() or q.lower() in idea.description.lower():
               filtered.append(idea)
    return filtered[:5]

@app.get("/api/newsletters", response_model=List[Newsletter])
async def get_newsletters():
    return sorted(list(db_newsletters.values()), key=lambda x: x.id, reverse=True)

@app.post("/api/newsletters", response_model=Newsletter)
async def create_newsletter(news_in: NewsletterBase):
    new_id = generate_id("NEWS")
    new_news = Newsletter(**news_in.dict(), id=new_id, timestamp="Just now")
    db_newsletters[new_id] = new_news
    save_data()
    return new_news

# ==========================================
# Serve Frontend & Assets
# ==========================================
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = full_path.strip("/")
    
    # 1. Serve Logo Images if requested
    if clean_path in ["CS_Wholesale_Grocers_logo.png", "CS_Wholesale_Grocers_logo.svg"]:
        img_path = os.path.join(base_dir, clean_path)
        if os.path.exists(img_path):
            return FileResponse(img_path)
        else:
            print(f"\n[!] MISSING FILE: The browser is looking for '{clean_path}' but it is not saved in your folder -> {base_dir}\n")
            raise HTTPException(status_code=404, detail="Image not found")

    # 2. Serve the React UI (index.html) for all other routes
    html_path = os.path.join(base_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
        
    return {"message": "API is running. Place index.html in the same directory to view the UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)