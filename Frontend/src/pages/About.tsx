import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Users } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <div className="container mx-auto px-4 pt-32 pb-24">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              About <span className="gradient-text">This Project</span>
            </h1>
          </div>

          <Card className="p-8 mb-8 bg-card border-border rounded-2xl card-shadow animate-slide-up">
            <div className="prose prose-invert max-w-none">
              <p className="text-lg text-muted-foreground leading-relaxed">
                The AI PR Reviewer combines heuristic static checks, Semgrep security scanning, and Qwen LLM reasoning 
                to produce actionable feedback for developers. Built with FastAPI, it can be integrated into CI/CD 
                pipelines or GitHub Actions for automated code review.
              </p>
            </div>
          </Card>

          <Card className="p-8 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20 rounded-2xl card-shadow animate-slide-up">
            <div className="flex items-center gap-3 mb-6">
              <Users className="h-6 w-6 text-primary" />
              <h2 className="text-2xl font-semibold">Contributors</h2>
            </div>
            
            <div className="space-y-4">
              <div className="p-4 bg-card/50 rounded-xl border border-border">
                <h3 className="font-semibold text-lg mb-1">Anand Ganesh</h3>
                <p className="text-muted-foreground">Lead Developer & AI Integration</p>
              </div>
              
              <div className="p-4 bg-card/50 rounded-xl border border-border">
                <h3 className="font-semibold text-lg mb-1">Team CodeMate</h3>
                <p className="text-muted-foreground">Frontend & UX Development</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default About;
