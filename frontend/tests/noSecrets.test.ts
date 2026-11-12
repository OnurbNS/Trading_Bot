import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const SRC_ROOT = join(__dirname, '..', 'src')

const FORBIDDEN = [
  /SUPABASE_SERVICE_ROLE_KEY/i,
  /service_role/i,
  /BEGIN (RSA |OPENSSH )?PRIVATE KEY/,
  /sk_live_[A-Za-z0-9]+/,
  /api[_-]?secret/i,
]

function listFiles(dir: string): string[] {
  const entries = readdirSync(dir)
  const files: string[] = []
  for (const entry of entries) {
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) {
      files.push(...listFiles(full))
    } else if (/\.(ts|tsx|css|html)$/.test(entry)) {
      files.push(full)
    }
  }
  return files
}

describe('Segurança do frontend', () => {
  it('não contém credenciais ou service role no código-fonte', () => {
    const files = listFiles(SRC_ROOT)
    expect(files.length).toBeGreaterThan(0)

    const offenders: string[] = []
    for (const file of files) {
      const content = readFileSync(file, 'utf8')
      for (const pattern of FORBIDDEN) {
        if (pattern.test(content)) {
          offenders.push(`${file} matches ${pattern}`)
        }
      }
    }

    expect(offenders).toEqual([])
  })

  it('só permite variável de ambiente pública VITE_API_BASE_URL', async () => {
    const apiSource = readFileSync(join(SRC_ROOT, 'lib', 'api.ts'), 'utf8')
    expect(apiSource).toContain('VITE_API_BASE_URL')
    expect(apiSource).not.toMatch(/SERVICE_ROLE/i)
    expect(apiSource).not.toMatch(/SECRET/i)
    expect(apiSource).not.toMatch(/PRIVATE/i)
  })
})
