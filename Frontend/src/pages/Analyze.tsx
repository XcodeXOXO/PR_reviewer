import { useState } from "react";
import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Github, Hash, Sparkles, Gauge, Lightbulb } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from "react-markdown";

interface Finding {
  file: string;
  line: number;
  severity: string;
  message: string;
  suggestion: string;
}

interface AnalysisResult {
  summary_markdown: string;
  findings: Finding[];
  quality_score: number;
}

const Analyze = () => {
  const [repo, setRepo] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [maxFindings, setMaxFindings] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repo || !prNumber) {
      toast({
        title: "Missing Information",
        description: "Please provide both repository and PR number.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      // Replace with your actual ngrok URL
      const response = await fetch("https://YOUR_NGROK_URL/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          provider: "github",
          repo: repo,
          pr_number: parseInt(prNumber),
          max_findings: maxFindings,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze PR");
      }

      const data = await response.json();
      setResults(data);
      
      toast({
        title: "Analysis Complete",
        description: "Your pull request has been analyzed successfully.",
      });
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Failed to analyze the pull request. Please check your inputs and try again.",
        variant: "destructive",
      });
      console.error("Analysis error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navigation />
      
      <div className="container mx-auto px-4 pt-32 pb-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Analyze <span className="gradient-text">Pull Request</span>
            </h1>
          </div>

          {/* Input Form */}
          <Card className="p-8 mb-8 bg-card border-border rounded-2xl card-shadow animate-slide-up">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold mb-2">Submit a GitHub Pull Request</h2>
              <p className="text-muted-foreground">Provide repository details and let the AI handle the rest.</p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="repo" className="flex items-center gap-2">
                  <Github className="h-4 w-4" />
                  GitHub Repository
                </Label>
                <Input
                  id="repo"
                  placeholder="e.g. pallets/flask"
                  value={repo}
                  onChange={(e) => setRepo(e.target.value)}
                  className="bg-input border-border rounded-xl"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="prNumber" className="flex items-center gap-2">
                  <Hash className="h-4 w-4" />
                  Pull Request Number
                </Label>
                <Input
                  id="prNumber"
                  type="number"
                  placeholder="e.g. 3154"
                  value={prNumber}
                  onChange={(e) => setPrNumber(e.target.value)}
                  className="bg-input border-border rounded-xl"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="maxFindings">Maximum Findings</Label>
                <Input
                  id="maxFindings"
                  type="number"
                  min="1"
                  max="50"
                  value={maxFindings}
                  onChange={(e) => setMaxFindings(parseInt(e.target.value))}
                  className="bg-input border-border rounded-xl"
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full gradient-bg hover:opacity-90 transition-opacity text-lg py-6 rounded-2xl"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin">⏳</span> Analyzing...
                  </span>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-5 w-5" />
                    Run AI Review
                  </>
                )}
              </Button>
            </form>
          </Card>

          {/* Tip Callout */}
          <Card className="p-6 mb-8 bg-primary/5 border-primary/20 rounded-2xl">
            <div className="flex gap-3">
              <Lightbulb className="h-6 w-6 text-primary flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-1">💡 Tip</h3>
                <p className="text-sm text-muted-foreground">
                  Use a real GitHub repository and PR number for live testing. Example: repo='pallets/flask', pr_number='3154'.
                </p>
              </div>
            </div>
          </Card>

          {/* Results Dashboard */}
          {results && (
            <div className="grid lg:grid-cols-2 gap-8 animate-fade-in">
              {/* Left Panel */}
              <div className="space-y-6">
                <Card className="p-6 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20 rounded-2xl card-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <Gauge className="h-6 w-6 text-accent" />
                    <h3 className="text-xl font-semibold">Code Quality Score</h3>
                  </div>
                  <div className="text-5xl font-bold gradient-text">
                    {results.quality_score}/100
                  </div>
                </Card>
                
                <Card className="p-6 bg-card border-border rounded-2xl card-shadow">
                  <h3 className="text-xl font-semibold mb-4">Summary</h3>
                  <div className="prose prose-invert max-w-none text-sm">
                    <ReactMarkdown>{results.summary_markdown}</ReactMarkdown>
                  </div>
                </Card>
              </div>

              {/* Right Panel */}
              <Card className="p-6 bg-card border-border rounded-2xl card-shadow">
                <h3 className="text-xl font-semibold mb-4">Findings Overview</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left p-3 font-semibold text-sm">File</th>
                        <th className="text-left p-3 font-semibold text-sm">Line</th>
                        <th className="text-left p-3 font-semibold text-sm">Severity</th>
                        <th className="text-left p-3 font-semibold text-sm">Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.findings.map((finding, index) => (
                        <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                          <td className="p-3 text-sm font-mono">{finding.file}</td>
                          <td className="p-3 text-sm">{finding.line}</td>
                          <td className="p-3">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              finding.severity === "high" ? "bg-destructive/20 text-destructive" :
                              finding.severity === "medium" ? "bg-yellow-500/20 text-yellow-500" :
                              "bg-blue-500/20 text-blue-500"
                            }`}>
                              {finding.severity}
                            </span>
                          </td>
                          <td className="p-3 text-sm">{finding.message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analyze;
