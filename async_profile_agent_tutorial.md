# Converting profileAgent to Async - Step-by-Step Tutorial

## 🎯 Goal
Transform the synchronous `profileAgent` class to use async/await for better performance when making multiple API calls.

## 📚 Key Concepts Before We Start

### What needs to be async?
✅ **I/O Operations** (waiting for external responses):
- Azure Search queries
- OpenAI API calls
- Web searches
- File operations (sometimes)

❌ **Keep Synchronous** (pure computation):
- String operations (replace, strip, etc.)
- List comprehensions
- Regular expressions
- PDF generation (CPU-bound)

---

## 🔄 Step 1: Update Class Initialization

### ❌ Before (Sync):
```python
def __init__(self, company_name, k, ...):
    self.search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, ...)
    self.az_openai = AzureOpenAI(azure_endpoint=AOAI_ENDPOINT, ...)
    self.web_openai = OpenAI(api_key=OPENAI_API_KEY)
```

### ✅ After (Async):
```python
def __init__(self, company_name, k, ...):
    # Use ASYNC clients instead
    self.search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, ...)  # Will use async methods
    self.az_openai = AsyncAzureOpenAI(azure_endpoint=AOAI_ENDPOINT, ...)  # Async!
    self.web_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)  # Async!
```

**📖 Teaching Point:**
- `__init__` stays synchronous (no `async def`)
- We just swap to async-compatible clients
- The actual async happens in the methods that USE these clients

---

## 🔄 Step 2: Convert Search Method to Async

### ❌ Before (Sync):
```python
def _retrieve_hybrid_enhanced(self, query_nl, k: int = 50, ...):
    results = sc.search(  # ⏳ Blocks while waiting
        search_text=self.bm25_creator(query_nl),
        vector_queries=[vq],
        ...
    )

    for r in results:  # ⏳ Blocks while iterating
        # process results
```

### ✅ After (Async):
```python
async def _retrieve_hybrid_enhanced(self, query_nl, k: int = 50, ...):
    # Notice: async def instead of def

    results = await sc.search(  # ⏳ Doesn't block! Other code can run
        search_text=self.bm25_creator(query_nl),
        vector_queries=[vq],
        ...
    )

    # If results is an async iterator:
    hits = []
    async for r in results:  # async for!
        # process results
        hits.append(r)
```

**📖 Teaching Points:**
1. **`async def`** - Marks the function as asynchronous
2. **`await`** - Pauses THIS function, lets other tasks run
3. **`async for`** - Like regular for, but for async iterators
4. Azure SDK may provide async methods - check their docs!

---

## 🔄 Step 3: Convert OpenAI Calls to Async

### ❌ Before (Sync):
```python
def _rag_answer(self, rag_nl, question, ...):
    # ... build context ...

    resp = client.chat.completions.create(  # ⏳ Blocks for 2-5 seconds
        model=AOAI_DEPLOYMENT,
        messages=messages,
        reasoning_effort="high"
    )
    answer = resp.choices[0].message.content
```

### ✅ After (Async):
```python
async def _rag_answer(self, rag_nl, question, ...):
    # ... build context (same as before) ...

    # Now we can await the API call
    resp = await client.chat.completions.create(  # ⏳ Non-blocking!
        model=AOAI_DEPLOYMENT,
        messages=messages,
        reasoning_effort="high"
    )
    answer = resp.choices[0].message.content
```

**📖 Teaching Points:**
- The method signature changes to `async def`
- Add `await` before the API call
- Everything else stays the same!
- While waiting for OpenAI, other code can run

---

## 🔄 Step 4: Chain Async Calls

### ❌ Before (Sync):
```python
def _rag_answer(self, rag_nl, question, ...):
    mode, hits = self._retrieve_hybrid_enhanced(...)  # Wait
    ctx_text, ctx_items = self._build_context(hits)    # Then wait
    resp = client.chat.completions.create(...)         # Then wait
```

### ✅ After (Async):
```python
async def _rag_answer(self, rag_nl, question, ...):
    # When calling async methods, use await
    mode, hits = await self._retrieve_hybrid_enhanced(...)  # Async call

    # Sync method stays the same (no await needed)
    ctx_text, ctx_items = self._build_context(hits)

    # Async API call
    resp = await client.chat.completions.create(...)
```

**📖 Teaching Points:**
- **Async calls async** = use `await`
- **Async calls sync** = no `await` needed
- Rule: If a method is `async def`, you must `await` it when calling

---

## 🔄 Step 5: The POWER - Concurrent Execution! ⚡

This is where async really shines!

### ❌ Before (Sync) - Sequential:
```python
def _sections(self, pairs):
    answers = []
    for q, r in pairs:  # One at a time
        resp = self._rag_answer(rag_nl=r[0], question=q[0])  # Wait 5 seconds
        answers.append(resp["answer"])
        time.sleep(5.0)  # Wait more
    return answers
    # If 5 pairs: 5 × (5s + 5s) = 50 seconds total! 😴
```

### ✅ After (Async) - Concurrent:
```python
async def _sections(self, pairs):
    # Create all tasks at once (don't start yet)
    tasks = []
    for q, r in pairs:
        task = self._rag_answer(rag_nl=r[0], question=q[0])
        tasks.append(task)

    # Run ALL tasks concurrently! 🚀
    answers = await asyncio.gather(*tasks)

    # Extract just the answer text
    return [resp["answer"] for resp in answers]
    # If 5 pairs: max(5s, 5s, 5s, 5s, 5s) = 5 seconds total! 🚀
```

**📖 Teaching Points:**
1. **`asyncio.gather(*tasks)`** - Runs all tasks at the same time
2. Instead of 5 × 5s = 25s, we do all in 5s (the longest one)
3. Massive speedup for multiple API calls!
4. This is the MAIN benefit of async!

---

## 🔄 Step 6: Helper Methods - Sync vs Async

### Keep Sync (Pure Computation):
```python
def _build_context(self, hits, ...):  # No async needed
    # Just processing data, no I/O
    lines = []
    for h in hits:
        text = h.get("text")
        lines.append(text)
    return "\n".join(lines)

def _company_filter(self):  # No async needed
    # Just string manipulation
    return f"company_name eq '{self.company_name}'"

def _generate_pdf(self, text):  # No async needed
    # CPU-bound, not I/O-bound
    # (though you COULD run in executor if it's slow)
```

**📖 Teaching Point:**
- If there's no `await` inside, no need for `async def`
- Keep simple functions simple!

---

## 🔄 Step 7: Retries with Async

### ❌ Before (Sync):
```python
while True:
    if tries > 0:
        time.sleep(3.0)  # ⏳ Blocks everything
    resp = self._rag_answer(...)
    if not has_na(resp) or tries >= max_retries:
        break
    tries += 1
```

### ✅ After (Async):
```python
while True:
    if tries > 0:
        await asyncio.sleep(3.0)  # ⏳ Non-blocking sleep!
    resp = await self._rag_answer(...)  # async call
    if not has_na(resp) or tries >= max_retries:
        break
    tries += 1
```

**📖 Teaching Points:**
- Use `asyncio.sleep()` instead of `time.sleep()`
- Must use `await` with asyncio.sleep
- Other tasks can run during the sleep

---

## 🎯 Summary: Conversion Checklist

When converting to async, ask these questions:

1. **Does this method make I/O calls?**
   - Yes → Make it `async def`
   - No → Keep it `def`

2. **Am I calling an async method?**
   - Yes → Use `await`
   - No → Call normally

3. **Are there multiple I/O operations that could run together?**
   - Yes → Use `asyncio.gather()`
   - No → Just use `await` sequentially

4. **Replace blocking operations:**
   - `time.sleep()` → `await asyncio.sleep()`
   - `requests.get()` → `await aiohttp.get()` or `await httpx.get()`
   - `for item in results` → `async for item in results` (if async iterator)

5. **Update clients:**
   - `OpenAI()` → `AsyncOpenAI()`
   - `AzureOpenAI()` → `AsyncAzureOpenAI()`

---

## 🚀 How to Call Async Methods

### In Jupyter/IPython:
```python
# Can use await directly
result = await agent._rag_answer("query", "question")
```

### In Regular Python Script:
```python
import asyncio

async def main():
    agent = profileAgent(...)
    result = await agent._rag_answer("query", "question")
    print(result)

# Run it
asyncio.run(main())
```

### From Sync Code (Bridge):
```python
import asyncio

def sync_function():
    agent = profileAgent(...)
    # Run async from sync
    result = asyncio.run(agent._rag_answer("query", "question"))
    return result
```

---

## 💡 Common Mistakes to Avoid

❌ Forgetting `await`:
```python
async def my_func():
    result = self._async_method()  # Returns coroutine, not result!
```

✅ Correct:
```python
async def my_func():
    result = await self._async_method()  # Actually waits and gets result
```

---

❌ Using `async def` without `await`:
```python
async def my_func():  # Warning: no async calls inside!
    x = 1 + 1
    return x
```

✅ If no async operations, keep it sync:
```python
def my_func():
    x = 1 + 1
    return x
```

---

❌ Sequential when you could be concurrent:
```python
async def slow():
    result1 = await api_call_1()  # Wait 3s
    result2 = await api_call_2()  # Wait 3s
    # Total: 6s
```

✅ Concurrent is faster:
```python
async def fast():
    result1, result2 = await asyncio.gather(
        api_call_1(),  # Both run together
        api_call_2()
    )
    # Total: 3s (max of the two)
```

---

## 🎓 Practice Exercise

Try converting this sync function yourself:

```python
def fetch_multiple_companies(self, company_numbers):
    results = []
    for num in company_numbers:
        data = self._rag_answer(f"Get info for {num}")
        results.append(data)
    return results
```

**Your turn!** Convert it to async with concurrent execution.

<details>
<summary>Click to see solution</summary>

```python
async def fetch_multiple_companies(self, company_numbers):
    # Create all tasks
    tasks = [
        self._rag_answer(f"Get info for {num}")
        for num in company_numbers
    ]

    # Run concurrently
    results = await asyncio.gather(*tasks)
    return results
```

</details>

---

Ready to see the full converted class? Let's do it! 🚀
