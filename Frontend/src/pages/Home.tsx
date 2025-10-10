import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import FeatureCard from "@/components/FeatureCard";
import { Bot, ShieldCheck, Rocket } from "lucide-react";
import { Card } from "@/components/ui/card";

const Home = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <Hero />
      
      {/* Features Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Why Choose <span className="gradient-text">AI Review?</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto animate-slide-up">
            <FeatureCard
              icon={Bot}
              title="AI-Powered Suggestions"
              description="Backed by Qwen 3-Coder via OpenRouter, providing contextual insights beyond simple lint checks."
            />
            <FeatureCard
              icon={ShieldCheck}
              title="Security & Style Checks"
              description="Integrates Semgrep and Python Static analyzers to identify real issues, not false alarms."
            />
            <FeatureCard
              icon={Rocket}
              title="Instant Results"
              description="Runs analysis and returns a full quality score and improvement suggestions in seconds."
            />
          </div>
        </div>
      </section>
      
      {/* Callout Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <Card className="max-w-4xl mx-auto p-8 md:p-12 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20 rounded-2xl card-shadow">
            <div className="text-center space-y-4">
              <h2 className="text-3xl md:text-4xl font-bold gradient-text">
                Integrated with FastAPI + OpenRouter + GitHub
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                This project unites static analysis with AI reasoning to automate the most time-consuming parts of code review.
              </p>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default Home;
