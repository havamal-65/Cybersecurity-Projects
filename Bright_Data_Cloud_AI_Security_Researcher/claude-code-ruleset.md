# Claude Code Application Development Ruleset

## 🎯 Core Principles

### 1. **NO SIMULATIONS OR MOCKS**
- **ALWAYS** implement real, working functionality
- **NEVER** create placeholder functions, mock data, or simulated outputs
- When doing TDD, explicitly state: "Be explicit about the fact that you're doing test-driven development so that it avoids creating mock implementations, even for functionality that doesn't exist yet"
- If unable to implement something real, ask for clarification or additional resources

### 2. **FOLLOW DIRECTIONS PRECISELY**
- Read and understand the full request before starting
- Ask clarifying questions if requirements are ambiguous
- Don't make assumptions about what the user wants
- Implement exactly what was requested, not what you think might be better

### 3. **VERIFY REAL IMPLEMENTATION**
- "At this stage, it can help to ask it to verify with independent subagents that the implementation isn't overfitting to the tests"
- Always test your code with real data and real scenarios
- Run the code to ensure it actually works
- Check edge cases and error conditions

---

## 📋 Pre-Development Workflow

### **1. EXPLORE Phase** (CRITICAL - Don't Skip!)
```
1. Read all relevant files in the codebase
2. Understand existing patterns and conventions
3. Research any unfamiliar concepts or APIs
4. DO NOT write any code in this phase
5. Ask: "Read [relevant files] and understand the current implementation"
```

### **2. PLAN Phase** (Use "think" keywords)
- "We recommend using the word "think" to trigger extended thinking mode"
- Thinking levels: `"think"` < `"think hard"` < `"think harder"` < `"ultrathink"`
- Create detailed step-by-step plan
- "Steps #1-#2 are crucial—without them, Claude tends to jump straight to coding a solution"

### **3. REVIEW Phase**
- Present the plan for approval
- Verify it addresses all requirements
- Ensure no mock implementations are planned

---

## 🛠️ Development Best Practices

### **Real Implementation Guidelines**

1. **Database Operations**
   - Use actual database connections
   - Implement real CRUD operations
   - Handle connection errors properly
   - Never return hardcoded data

2. **API Integrations**
   - Make real HTTP requests
   - Handle authentication properly
   - Implement proper error handling
   - Parse real responses

3. **File Operations**
   - Actually read/write files
   - Handle file system errors
   - Use proper paths and permissions
   - Never simulate file contents

4. **User Interfaces**
   - Create functional components
   - Implement real event handlers
   - Connect to real backend services
   - "Claude performs best when it has a clear target to iterate against—a visual mock, a test case, or another kind of output"

### **Testing Approach**

1. **Test-Driven Development (TDD)**
   - "The robots LOVE TDD. Seriously. They eat it up"
   - Write tests first with expected real outputs
   - Implement real functionality to pass tests
   - Never write tests that always pass

2. **Verification Steps**
   ```bash
   # Always run after implementation:
   npm test           # or appropriate test command
   npm run typecheck  # type checking
   npm run lint       # linting
   prettier --write . # formatting
   ```

---

## 📁 CLAUDE.md Configuration

Create a `CLAUDE.md` file in your project root with:

```markdown
# Project: [Your Project Name]

## CRITICAL RULES

### NO MOCKS OR SIMULATIONS
- ALWAYS implement real, working functionality
- NEVER create placeholder functions or mock data
- If you cannot implement something real, ASK for clarification
- Verify all implementations actually work before committing

### FOLLOW SPECIFICATIONS EXACTLY
- Read the full request before starting
- Implement exactly what was requested
- Don't add features that weren't asked for
- Ask questions if requirements are unclear

## Project Context
[Brief description of what the project does]

## Architecture Decisions
[Document key technical choices and why they were made]

## Code Standards
- [Your coding standards]
- [Naming conventions]
- [File organization]

## Testing Requirements
- All new features must have tests
- Tests must use real data, not mocks
- Run tests before committing

## Common Commands
```bash
npm run dev      # Start development server
npm test         # Run tests
npm run build    # Build for production
```

## Error Handling
- Always handle errors gracefully
- Log errors with context
- Provide user-friendly error messages
- Never silently fail

## Security Considerations
- [Your security requirements]
- Never commit sensitive data
- Use environment variables for secrets
```

---

## 🔒 Security & Safety

### **Permission Requirements**
- "Claude Code uses strict read-only permissions by default"
- Always request permission for:
  - File modifications
  - Running commands
  - Git operations
  - External API calls

### **Trust Verification**
- "First-time codebase runs and new MCP servers require trust verification"
- Review all commands before execution
- Be cautious with external integrations

---

## 🚀 Advanced Techniques

### **Complex Tasks**
- Use `--enable-architect` flag for large refactoring
- "I can see myself parallelizing the work using git worktrees"
- Break large tasks into smaller, verifiable chunks

### **Visual Development**
- "Claude excels with images and diagrams"
- Provide mockups for UI development
- Use screenshots for iterative refinement
- Implement the actual UI, not a simulation

### **Debugging Workflow**
```bash
# Redirect output to log file for Claude to read
npm run dev > dev.log 2>&1

# In another session
claude -p "Read dev.log and help me debug the error"
```

---

## 🎮 Custom Commands

Create `.claude/commands/` directory with custom commands:

**`.claude/commands/no-mocks.md`:**
```markdown
REMINDER: You must implement REAL functionality, not mocks or simulations.
- All database calls must connect to real databases
- All API calls must make real HTTP requests
- All file operations must actually read/write files
- All UI components must be fully functional
$ARGUMENTS
```

**`.claude/commands/verify-real.md`:**
```markdown
Verify that the implementation:
1. Contains NO mock functions or simulated data
2. Actually works when run
3. Handles real-world edge cases
4. Has proper error handling
Run the code and test with real inputs: $ARGUMENTS
```

---

## ⚡ Quick Reference Checklist

Before starting any task:
- [ ] Read existing code (EXPLORE phase)
- [ ] Create detailed plan (PLAN phase with "think")
- [ ] Get plan approval
- [ ] Implement REAL functionality only
- [ ] Test with real data
- [ ] Handle errors properly
- [ ] Run linting and formatting
- [ ] Verify it actually works
- [ ] Commit with descriptive message

## 🚨 Red Flags to Avoid

- Hardcoded return values
- Functions that don't actually do anything
- Placeholder comments like "// TODO: Implement later"
- Test data instead of real data
- Simulated delays or fake loading states
- Mock API responses
- "Reward hacking: when the AI takes shortcuts to make it look like it succeeded without actually solving the problem"

---

