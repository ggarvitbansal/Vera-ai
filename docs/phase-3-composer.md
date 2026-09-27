# Phase 3: High-Compulsion Prompt Engine & Vertical Composers

## Objectives
1. Build vertical-specialized composition modules for each of the 5 core domains:
   - **Dentists**: Clinical-peer tone, peer-to-peer vocabulary, source citations (JIDA, DCI), strict taboo avoidance (no "guaranteed", no "100% cure", no "painless").
   - **Salons**: Warm, fellow-operator, practical service+price framing ("Haircut @ ₹99", "Bridal Skin Prep @ ₹2,499"), seasonal & wedding countdown hooks.
   - **Restaurants**: Operator-to-operator language, covers shift, delivery vs dine-in logic, event dynamics (IPL match nights, corporate bulk thalis).
   - **Gyms**: Motivational coach, evidence-based, zero shame on lapsed members ("happens to everyone, no judgment"), seasonal reframe, free trial reservation.
   - **Pharmacies**: Trustworthy, precise, scientific molecule names, batch recall handling, respectful tone for seniors (*"Namaste"*, dosage verifications).
2. **Context Provenance & Zero Hallucination**:
   - Every number (views, review count, delta %, trial n, batch ID, member count) must strictly originate from `TriggerContext`, `MerchantContext`, or `CategoryContext`.
   - Any ungrounded factual claim is blocked.
3. **Language Code-Mixing**:
   - Detect `hi` or `hi-en mix` in merchant/customer identity and seamlessly output natural Hinglish (*"Apke liye 2 slots ready hain"*, *"Samajh gayi"*, *"khatam hongi"*).
4. **Cialdini Compulsion Engineering**:
   - **Social Proof**: Locality peer benchmarks (*"3 clinics in Lajpat Nagar..."*).
   - **Loss Aversion**: Missed searches or upcoming recall expirations.
   - **Effort Externalization**: Complete artifact already drafted (*"Want me to send the 90-sec draft? Takes 2 min. Reply YES."*).
   - **Single Binary CTA**: Reply YES/STOP, or binary option selection (1 vs 2).
5. **Hybrid Architecture**:
   - Optional frontier LLM integration (OpenAI, Gemini, Anthropic, DeepSeek, Groq) via environment configuration.
   - Deterministic rule-based vertical synthesizer fallback for ultra-fast, zero-cost, zero-hallucination compliance.

---

## File Structure
- `composer.py`: Main entry point for `compose(category, merchant, trigger, customer?) -> dict`.
- `verticals/`: Modular domain engines:
  - `dentists.py`
  - `salons.py`
  - `restaurants.py`
  - `gyms.py`
  - `pharmacies.py`
- `guardrails.py`: Taboo checking, validation, and single CTA enforcement.
